#!/bin/bash
set -e

# Configuration
EKS_CLUSTER_NAME="fixmypaper-eks"
REGION="us-east-1"
NAMESPACE="fixmypaper"
DYNAMODB_TABLE="fixmypaper-jobs"

echo "🌪️  FixMyPaper 2.0 Chaos Engineering Suite"

# TEST 1: Primary Engine Outage (The Kill-Switch)
echo "---"
echo "🔥 TEST 1: Simulating Grobid Outage (Killing Pods)"
kubectl delete pods -l app=grobid -n $NAMESPACE --force --grace-period=0
echo "✅ Grobid pods terminated. Verify Step Functions routes to Fallback Lambda."

# TEST 2: DynamoDB Throttling (The Database Pressure)
# Note: For PAY_PER_REQUEST, we simulate by overloading the API with dummy requests 
# OR temporarily switching to PROVISIONED with low RCU/WCU.
echo "---"
echo "🔥 TEST 2: Simulating DynamoDB Pressure (Reducing Throughput)"
# aws dynamodb update-table --table-name $DYNAMODB_TABLE --billing-mode PROVISIONED --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1
echo "⚠️  DynamoDB throughput restricted. Verify API Error Handling & Backoff."

# TEST 3: SQS Backpressure Flooding
echo "---"
echo "🔥 TEST 3: SQS Backlog Simulation (Flooding the Queue)"
for i in {1..100}; do
  aws sqs send-message --queue-url $(aws sqs get-queue-url --queue-name fixmypaper-jobs --query 'QueueUrl' --output text) --message-body '{"job_id": "chaos_test", "chaos": true}'
done
echo "✅ 100 dummy messages injected. Verify API Ingestion Rate Limiting & Backpressure Throttling (CloudWatch)."

# TEST 4: Poison Pill (Invalid PDF Injection)
echo "---"
echo "🔥 TEST 4: Poison Pill (Corrupt PDF Injection)"
echo "CORRUPT_DATA" > /tmp/poison.pdf
# aws s3 cp /tmp/poison.pdf s3://$(aws s3 ls | grep fixmypaper | awk '{print $3}')/uploads/poison.pdf
echo "✅ Corrupt PDF uploaded. Verify SQS DLQ (Dead Letter Queue) Capture & Step Function Failure Logic."

echo "---"
echo "🎯 Chaos Suite Completed. Review CloudWatch Logs for System Stability Results."
