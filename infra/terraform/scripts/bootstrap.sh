#!/bin/bash
set -e

# FixMyPaper 2.0 Infrastructure Bootstrap Script
# This script initializes Terraform for the first time in the 2.0 environment.

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Initializing FixMyPaper 2.0 Infrastructure Bootstrap...${NC}"

# Check for AWS CLI
if ! command -v aws &> /dev/null
then
    echo -e "${RED}❌ Error: AWS CLI not found. Please install it first.${NC}"
    exit 1
fi

# Check if terraform is installed
if ! command -v terraform &> /dev/null
then
    echo -e "${RED}❌ Error: Terraform not found. Please install it first.${NC}"
    exit 1
fi

cd "$(dirname "$0")/.."

echo -e "${GREEN}📦 Initializing Terraform...${NC}"
terraform init

# Create and select a 'production' workspace if it doesn't exist
WORKSPACE="production"
if ! terraform workspace list | grep -q "$WORKSPACE"; then
    echo -e "${GREEN}🆕 Creating workspace: $WORKSPACE...${NC}"
    terraform workspace new "$WORKSPACE"
else
    echo -e "${GREEN}🔄 Selecting workspace: $WORKSPACE...${NC}"
    terraform workspace select "$WORKSPACE"
fi

echo -e "${GREEN}🔍 Validating Configuration...${NC}"
terraform validate

echo -e "${GREEN}📝 Generating Plan (this will NOT apply changes yet)...${NC}"
terraform plan -out=tfplan

echo -e "--------------------------------------------------------"
echo -e "${GREEN}✅ Bootstrap Complete!${NC}"
echo -e "Review the plan above. To apply changes, run:"
echo -e "    ${BOLD}terraform apply tfplan${NC}"
echo -e "--------------------------------------------------------"
