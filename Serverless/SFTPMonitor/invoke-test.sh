#!/bin/bash
$awsProfile=''
$secretARN=''
$secretName=''
$subnet1=''
$subnet2=''
$region='us-east-1'


sam build .

sam deploy  --profile $awsProfile \
--parameter-overrides SecretARN $secretARN SecretName $secretName Subnet1 $subnet1 Subnet2 $subnet2 Region $region\
--capabilities CAPABILITY_IAM \
--guided



