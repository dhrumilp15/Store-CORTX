import os
import discord
from dotenv import load_dotenv
from pathlib import Path
import boto3
from upload_to_s3 import upload_to_s3
from elasticsearch_conn import ElasticSearchConnector

env_path = Path('.') / '.env'

load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

s3_client = boto3.client(
    's3', endpoint_url=str(os.getenv('ENDPOINT_URL')),
    aws_access_key_id=str(os.getenv('AWS_ACCESS_KEY_ID')),
    aws_secret_access_key=str(os.getenv('AWS_SECRET_ACCESS_KEY'))
)

es_client = ElasticSearchConnector(
    elastic_domain=os.getenv("ELASTIC_DOMAIN"),
    elastic_port=os.getenv("ELASTIC_PORT"),
    index='file_index'
)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message: discord.Message):
    '''Send all message attachments to the CORTX s3 bucket'''
    if message.author == client.user:
        return

    await upload_to_s3(s3_client, es_client, message)

    if message.content.startswith('!search') or message.content.startswith('!s'):
        message.content = ''.join(message.content.split()[1:])
        print(es_client.search(message.content))

client.run(TOKEN)
