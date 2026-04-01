import { NextResponse } from "next/server";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, ScanCommand, PutCommand, DeleteCommand } from "@aws-sdk/lib-dynamodb";
import { v4 as uuidv4 } from "uuid";

export const runtime = "nodejs";

const config = {
  region: process.env.APP_AWS_REGION || "us-east-1",
  credentials: {
    accessKeyId: process.env.APP_AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.APP_AWS_SECRET_ACCESS_KEY,
  },
};

const ddbClient = DynamoDBDocumentClient.from(new DynamoDBClient(config));
const TABLE = "fixmypaper-formats"; // Fallback to provided name

export async function GET() {
  try {
    const { Items } = await ddbClient.send(new ScanCommand({
      TableName: process.env.DYNAMODB_TABLE_FORMATS || TABLE,
    }));
    return NextResponse.json(Items || []);
  } catch (error) {
    console.error("Formats GET error:", error);
    return NextResponse.json({ error: "Failed to fetch formats" }, { status: 500 });
  }
}

export async function POST(request) {
  try {
    const body = await request.json();
    const formatId = uuidv4();
    
    const item = {
      format_id: formatId,
      ...body,
      created_at: new Date().toISOString(),
    };

    await ddbClient.send(new PutCommand({
      TableName: process.env.DYNAMODB_TABLE_FORMATS || TABLE,
      Item: item,
    }));

    return NextResponse.json(item);
  } catch (error) {
    console.error("Formats POST error:", error);
    return NextResponse.json({ error: "Failed to create format" }, { status: 500 });
  }
}

export async function DELETE(request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get("id");

  if (!id) return NextResponse.json({ error: "Missing ID" }, { status: 400 });

  try {
    await ddbClient.send(new DeleteCommand({
      TableName: process.env.DYNAMODB_TABLE_FORMATS || TABLE,
      Key: { format_id: id },
    }));
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Formats DELETE error:", error);
    return NextResponse.json({ error: "Failed to delete format" }, { status: 500 });
  }
}
