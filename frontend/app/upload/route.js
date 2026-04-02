import { NextResponse } from "next/server";
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, PutCommand } from "@aws-sdk/lib-dynamodb";
import { SFNClient, StartExecutionCommand } from "@aws-sdk/client-sfn";
import { v4 as uuidv4 } from "uuid";
export const runtime = "nodejs";

// AWS Configuration
const config = {
  region: process.env.APP_AWS_REGION || "us-east-1",
  credentials: {
    accessKeyId: process.env.APP_AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.APP_AWS_SECRET_ACCESS_KEY,
  },
};

const s3Client = new S3Client(config);
const ddbClient = DynamoDBDocumentClient.from(new DynamoDBClient(config));
const sfnClient = new SFNClient(config);

export async function POST(request) {
  const S3_BUCKET = process.env.S3_BUCKET_NAME;
  const DYNAMODB_TABLE = process.env.DYNAMODB_TABLE_JOBS;
  const SFN_ARN = process.env.STEP_FUNCTION_ARN;

  if (!S3_BUCKET || !DYNAMODB_TABLE) {
    return NextResponse.json({ error: "Missing AWS Configuration. Check S3_BUCKET_NAME and DYNAMODB_TABLE_JOBS in your .env" }, { status: 500 });
  }

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

    const arrayBuffer = await file.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    // 0. PDF Validation Layer (Strict Edge Security)
    const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20 MB

    if (buffer.length > MAX_FILE_SIZE) {
      return NextResponse.json({ error: "File exceeds 20MB limit." }, { status: 400 });
    }

    // Genuine PDFs must begin with the %PDF- magic bytes signature
    if (buffer.length < 5 || buffer.toString("utf-8", 0, 5) !== "%PDF-") {
      return NextResponse.json({ error: "Invalid file format. Genuine PDF required." }, { status: 400 });
    }

    // The heavy text parsing is delegated to the robust Python Lambdas 
    // to avoid Next.js Webpack and memory crashes.
    let validationStatus = "valid";

    // 1. Upload to S3

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
        validation_status: validationStatus,
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
        skip_complex_modules: validationStatus === "warning"
      }),
    }));

    return NextResponse.json({ 
      job_id: jobId, 
      status: "pending",
      validation_status: validationStatus
    });
  } catch (error) {
    console.error("Upload error:", error);
    return NextResponse.json({ 
      error: "Serverless upload failed", 
      details: error.message 
    }, { status: 500 });
  }
}
