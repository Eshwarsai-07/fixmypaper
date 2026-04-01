import { NextResponse } from "next/server";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, GetCommand } from "@aws-sdk/lib-dynamodb";

export const runtime = "nodejs";

const config = {
  region: process.env.AWS_REGION || "us-east-1",
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  },
};

const ddbClient = DynamoDBDocumentClient.from(new DynamoDBClient(config));

export async function GET(request, { params }) {
  const jobId = params.jobId;
  const userId = "anonymous"; // Replace with actual user context if using auth
  const table = process.env.DYNAMODB_TABLE_JOBS;

  try {
    const { Item } = await ddbClient.send(new GetCommand({
      TableName: table,
      Key: {
        job_id: jobId,
        user_id: userId,
      },
    }));

    if (!Item) {
      return NextResponse.json({ error: "Job not found" }, { status: 404 });
    }

    return NextResponse.json(Item);
  } catch (error) {
    console.error("Status error:", error);
    return NextResponse.json({ 
      error: "Failed to fetch status", 
      details: error.message 
    }, { status: 500 });
  }
}
