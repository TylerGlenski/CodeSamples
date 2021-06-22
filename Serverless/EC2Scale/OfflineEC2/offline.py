import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import logging


# logging setup
logging_level = int(os.getenv('INFO'))
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging_level)



def lambda_handler(event, context):
    region = 'us-east-1'
    instance_ids = ['', '', ''] 
       
    ec2 = boto3.client('ec2', region_name=region)

    try:
        response = ec2.stop_instances(InstanceIds=instance_ids, DryRun=False)

        log_msg = "{ 'Instances': [ "
        for i in instance_ids:
            log_msg += f"{i}, "
        log_msg += '], '
        time = datetime.now(tz=None)
        log_msg += f" 'action': stopped, 'time': {str(time)}"
        log_msg += " }"
        logger.info(f"{log_msg} ")

        return 1
        
    except ClientError as e:
        logger.critical(f"ClientError Exception: {e}")
        raise e
    except Exception as err:
        logger.critical(f"Exception: {err}")
        raise err



if __name__ == "__main__":
    lambda_handler('','')