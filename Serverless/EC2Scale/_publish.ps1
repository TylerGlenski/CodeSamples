$stackName='' 
$awsProfile='' #aws profile for credentials
$region='us-east-1' # region deploying serverless app to
$templatePath='.aws-sam/build/template.yaml' # template filepath for cloudformation generated after build
$bucketName='' #bucket name to store source code
$s3Prefix='Serverless/EC2Scale'
## build
sam build 
## deploy
sam deploy `
--region $region `
--profile $awsProfile `
--template-file $templatePath `
--stack-name $stackName `
--s3-bucket $bucketName `
--s3-prefix $s3Prefix `
--capabilities CAPABILITY_IAM

