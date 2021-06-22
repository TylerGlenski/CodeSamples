import os
import boto3
from botocore.exceptions import ClientError
import logging
from datetime import datetime


# logging setup
logging_level = int(os.getenv('INFO'))
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging_level)

class DnsException(Exception):
    """Exception raised for dns errors/exceptions
    Attributes:
        error_type -- string the type of the error
        message -- string explanation of error and/or error code
    """
    def __init__(self, error_type='', message='DNS Error:'):
        
        self.error_type = error_type
        self message = message
        
        if error_type == 'update':
            self message += 'DNS Failed to update'
        else:
            self message += 'Generic DNS error'
            
        super().__init__(self.message)


def send_alert(payload):
    # send alert to alerting app/ticketing system that an error has occured with application
    print(f'Alert Sent: payload={payload}')


def get_instance_ip(instance_id):
    # input is a single ec2 instance id
    ## returns the instance IP for that specific instance

    try:
        ec2_client = boto3.client("ec2", region_name="us-east-1")
        reservations = ec2_client.describe_instances(InstanceIds=[instance_id]).get("Reservations")
        instance_ip = ""

        for reservation in reservations:
            for instance in reservation['Instances']:
                instance_ip = instance.get("PublicIpAddress")

        return instance_ip

    except Exception as e:
        logger.critical(e)
        raise e


def update_dns(instance_ips, zone_id, name):
    # input is the public IP's of the app servers staying online.
    ### Those public IP's will replace the records in the DNS record, removing the other records not included.

    record_type = 'A'
    records = []

    for ip in instance_ips:
        records.append({"Value": str(ip)})

    try:
        client = boto3.client('route53')
        response = client.change_resource_record_sets(
        HostedZoneId=zone_id,
        ChangeBatch= {
                        'Comment': 'add %s -> %s' % (name, 'records'),
                        'Changes': [
                            {
                             'Action': 'UPSERT',
                             'ResourceRecordSet': {
                                 'Name': name,
                                 'Type': record_type,
                                 'TTL': 300,
                                 'ResourceRecords': records
                            }
                        }]
        })
        time = datetime.now(tz=None)
        log_msg = "{ "
        log_msg += f"'records': {records}, 'record_name': {name}, 'action': UPSERT, 'time': {str(time)}"
        log_msg += " }"
        logger.info(log_msg)
    except Exception as e:
        payload = f"records: {records}, record_name: {name}, error: {e}"
        logger.critical(payload)
        error_type = 'update'
        send_alert(payload)
        raise DnsException(error_type)


def lambda_handler(event, context):
    zone_id = str(os.getenv('ZONE_ID'))
    record_name = str(os.getenv('RECORD_NAME'))

    try:
        instance_ids = ['i-0000', 'i-0000', 'i-0000'] # placeholders(paste yours in)
        instance_ips = []
        for instance in instance_ids:
            instance_ip = get_instance_ip(instance)
            instance_ips.append(instance_ip)
        update_dns(instance_ips=instance_ips, zone_id=zone_id, name=record_name)
        return 1
    except Exception as e:
        logger.critical(f"Exception: {e}")
        raise e


if __name__ == "__main__":
    lambda_handler('','')