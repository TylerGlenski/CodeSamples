# Introduction 
TODO: README things to do
1.  Description of each lambda within App.
2. Description of template/infrastrucre/deployment


## BEFORE DEPLOYING/PUBLISHING 
#### Make sure to update and/or validate the fields in samconfig.toml AND Publish.ps1 


#### publish script
  * Deployment Command PowerShell:
    * `./_publish.ps1`
    * OR `sam build `  Then  `sam deploy --guided` For a guided deployment.
  * Then script will run sam build and sam deploy commands
  * Deployment Command linux:
    * `pwsh ./_publish.ps1`
 