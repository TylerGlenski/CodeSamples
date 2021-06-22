import os
import boto3
from botocore.exceptions import ClientError
import logging
import time
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
    region = 'us-east-1'
    ec2_client = boto3.client("ec2", region_name=region)
    reservations = ec2_client.describe_instances(InstanceIds=[instance_id]).get("Reservations")
    instance_ip = ""

    for reservation in reservations:
        for instance in reservation['Instances']:
            instance_ip = instance.get("PublicIpAddress")

    return instance_ip


def update_dns(instance_ips, zone_id, name):
    # input is the public IP's of the EC2 instances staying online.
    # Those public IP's will replace the records in the DNS record, removing the other records not included.

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

    all_instances = ['i-00000', 'i-00000', 'i-0a00', 'i-00000', 'i-00000', 'i-00000', 'i-00000'] # All ec2 instances (placeholders paste yours in) to update main DNS listing

    # individual dns listing name + instance ID / listings are for support to RDP listing.hostedzone.com for support rdp endpoint as seen in route53
    online_ids = {'alpha': 'i-00000', 'beta': 'i-00000', 'gamma': 'i-00000', 'delta': 'i-00000'}

    zone_id = str(os.getenv('ZONE_ID'))
    record_name = str(os.getenv('RECORD_NAME')) 
    region="us-east-1"
    hosted_zone = 'mywebsite.com' # add in hosted zone such as 'mywebsite.com'

    ec2 = boto3.client('ec2', region_name=region)

    try:

        instance_ids = []
        for k in online_ids:
            instance_ids.append(online_ids[k])

        response = ec2.start_instances(InstanceIds=instance_ids)

        ec2_time = datetime.now(tz=None)
        log_msg = "{ 'records': [ "

        for k in online_ids:
            log_msg += f"'value': {online_ids[k]}, "

        log_msg += f"], 'action': StartInstances, 'time': {str(ec2_time)}, "
        log_msg += f" EC2 Response: {response} "
        log_msg += "}"
        logger.info(log_msg)

        time.sleep(20) # Gives ec2 time to start the instance.
        instance_ips = []
        for instance in all_instances:
            instance_ip = get_instance_ip(instance)
            instance_ips.append(instance_ip)

        for key in online_ids:
            name = f"{key}.{hosted_zone}"
            ip = get_instance_ip(online_ids[key])
            instance_ip = [ip]
            update_dns(instance_ips=instance_ip, zone_id=zone_id, name=name) # individuals DNS

        update_dns(instance_ips=instance_ips, zone_id=zone_id, name=record_name) # Main DNS

        return 1

    except Exception as e:
            logger.critical(f"{e}")
            raise e


if __name__ == "__main__":
    lambda_handler('','')