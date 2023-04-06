#!/bin/sh
STACK_NAME="ggr-selenoid"
SECONDS=0

echo "Starting to create AWS Cloudformation Stack: ${STACK_NAME}"

aws cloudformation create-stack \
--template-body file://cloudformation-ggr-selenoid.yml \
--stack-name $STACK_NAME \
--capabilities CAPABILITY_NAMED_IAM \
--parameters file://params.json

echo "Waiting for [$STACK_NAME] stack creation..."

aws cloudformation wait stack-create-complete \
--stack-name ${STACK_NAME} \
--output text

echo "Stack with name ${STACK_NAME} was created successfully!"
duration=$SECONDS
echo "After $(($duration / 60)) minutes and $(($duration % 60)) seconds."