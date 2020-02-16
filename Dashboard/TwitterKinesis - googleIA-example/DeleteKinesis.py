import boto3
import sys
from botocore.exceptions import ClientError



def delete_stream(client, stream_name):
   try:
        return client.delete_delivery_stream(DeliveryStreamName=stream_name)
        print('Successfully delete kinesis stream: {}'.format(stream_name))
   except:
        print('Kinesis {} does not exist'.format(stream_name))

def main(stream_name):
  client = boto3.client('firehose', region_name='us-east-1')
  delete_stream(client,stream_name)


if __name__ == '__main__':
    main(sys.argv[1])