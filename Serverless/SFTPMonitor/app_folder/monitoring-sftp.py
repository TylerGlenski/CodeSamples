import os
import boto3
import base64
from botocore.exceptions import ClientError
import json
import socket
import logging
import opsgenie_sdk
from opsgenie_sdk.rest import ApiException
import paramiko

# logging setup
logging_level = int(os.getenv('CRITICAL'))
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging_level)



def check_connection(input_hostname, input_port, input_user, input_pass):
    # Checks a SFTP connection, returns response from SFTP client
    # raises exception on error for lambda handler to handle NOT returning response
    
    connection_timeout = 10 # custom timeout for connection
    response = "SFTP Response: "

    # builds a networking socket for the sftp client to connect to. 
    sftp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sftp_socket.settimeout(connection_timeout)

    try:
        sftp_socket.connect((str(input_hostname), int(input_port)))
        client = paramiko.Transport((sftp_socket))
        client.connect(username=input_user, password=input_pass)

        sftp = paramiko.SFTPClient.from_transport(client)
        sftp.chdir('/') 

        # dirlist on remote host --> built into string
        dir_list = sftp.listdir('.')
        for dir in dir_list:
            response += f" /{str(dir)}"

        # closes connections
        sftp.close()
        client.close()

        return response

    except Exception as e:
        raise e


def create_alert(input_error, input_api, system_prefix):
    # Creates an OpsGenie alert and POST an alert to OpsGenie API 
    # No Return value but will raise exception to lambda handler to handle.

    try:
        # Configure API key authorization: GenieKey
        configuration = opsgenie_sdk.Configuration()
        configuration.api_key['Authorization'] = str(input_api)

        # create an instance of the API class
        api_instance = opsgenie_sdk.AlertApi(opsgenie_sdk.ApiClient(configuration))
        
        # this is where you build the alert params to send to OpsGenie
        create_alert_payload = opsgenie_sdk.CreateAlertPayload(
            message=f"{input_error}",
            alias=f"{system_prefix}-sftp-timeout",
            priority="P2"
        ) 

        logger.info('Sending failed conenction alert to OpsGenie') # log action
        
        api_instance.create_alert(create_alert_payload) # Create Alert
        
        logger.info('OpsGenie Alert POST Successful:') # log outcome
    
    except ApiException as e:
        logger.critical(f"Exception when calling AlertApi->create_alert: {e} ") # logs the api exception.
        raise e
    except Exception as e:
        logger.critical(f"Exception when configuring API: {e} ") # logs the configuration exception.
        raise e


def get_secret():
    # Gets the secrets variables from AWS secret manager
    # if secret string param in secrets manager @ secret_name will return JSON OBJ
    # if base 64 encoded will return the secret binary from aws secrets manger secret_name

    secret_name = os.getenv("SECRET_NAME")
    region_name = os.getenv("REGION")

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )


    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            
    if secret:        
        return json.loads(secret)
    elif decoded_binary_secret:
        return decoded_binary_secret
    else:
        return f"No Secret found"
    


def lambda_handler(event, context):
    # MAIN function
    # On connection failure sends alert to OpsGenie
    # On OpsGenie error, after connection error, exceptions out the lambda raising error to lambda console.
    
    secret_vars = get_secret()
    genie_api = secret_vars['OPSGENIE_API']
    username = secret_vars['USERNAME'] 
    password =  secret_vars['PASSWORD'] 
    hostname = secret_vars["HOSTNAME"]
    port = secret_vars["PORT"]
    system_prefix = secret_vars["SYSTEM_PREFIX"]

    try:
        logger.info(f'Checking Connection to {system_prefix} at: {hostname} ')
        response = check_connection(hostname, port, username, password)
        return response
    except Exception as connection_error:
        try:
            alert_error = f"{system_prefix}-SFTP-Connection Critical Error: {connection_error} : {hostname}"
            create_alert(alert_error, genie_api, system_prefix)
            logger.critical(alert_error)
            return alert_error 
        except Exception as genie_error:
            raise genie_error
             

if __name__ == "__main__":
    lambda_handler('','')
         




    
