import { NextResponse } from "next/server";
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, PutCommand } from "@aws-sdk/lib-dynamodb";
import { SFNClient, StartExecutionCommand } from "@aws-sdk/client-sfn";
import { v4 as uuidv4 } from "uuid";

export const runtime = "nodejs";

// AWS Configuration
const config = {
  region: process.env.AWS_REGION || "us-east-1",
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  },
};

const s3Client = new S3Client(config);
const ddbClient = DynamoDBDocumentClient.from(new DynamoDBClient(config));
const sfnClient = new SFNClient(config);

export async function POST(request) {
  const S3_BUCKET = process.env.S3_BUCKET_NAME;
  const DYNAMODB_TABLE = process.env.DYNAMODB_TABLE_JOBS;
  const SFN_ARN = process.env.STEP_FUNCTION_ARN;

  try {
    const incoming = await request.formData();
    const file = incoming.get("file");
    const formatId = incoming.get("format_id");

    if (!file) {
      return NextResponse.json({ error: "No file uploaded" }, { status: 400 });
    }

    const jobId = uuidv4();
    const userId = "anonymous"; // Replace with actual user context if using auth
    const fileName = file.name || "upload.pdf";
    const s3Key = `uploads/${jobId}_${fileName}`;

    // 1. Upload to S3
    const arrayBuffer = await file.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    await s3Client.send(new PutObjectCommand({
      Bucket: S3_BUCKET,
      Key: s3Key,
      Body: buffer,
      ContentType: file.type || "application/pdf",
    }));

    // 2. Initialize Job in DynamoDB
    await ddbClient.send(new PutCommand({
      TableName: DYNAMODB_TABLE,
      Item: {
        job_id: jobId,
        user_id: userId,
        status: "pending",
        filename: fileName,
        s3_key: s3Key,
        created_at: new Date().toISOString(),
      },
    }));

    // 3. Trigger Step Function Workflow
    await sfnClient.send(new StartExecutionCommand({
      stateMachineArn: SFN_ARN,
      input: JSON.stringify({
        job_id: jobId,
        user_id: userId,
        s3_key: s3Key,
      }),
    }));

    return NextResponse.json({ job_id: jobId, status: "pending" });
  } catch (error) {
    console.error("Upload error:", error);
    return NextResponse.json({ 
      error: "Serverless upload failed", 
      details: error.message 
    }, { status: 500 });
  }
}
