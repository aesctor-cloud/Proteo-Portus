import psycopg2
import logging
import os
from dotenv import load_dotenv

def get_database():

    logging.basicConfig(level=logging.INFO)

    load_dotenv()

    RDS_HOST = os.environ['RDS_HOST']
    RDS_PORT = os.environ['RDS_PORT']
    RDS_USER = os.environ['RDS_USER']
    RDS_PASSWORD = os.environ['RDS_PASSWORD']
    RDS_DB = os.environ['RDS_DB']


    conn = psycopg2.connect(
        host=RDS_HOST,
        port=RDS_PORT,
        user=RDS_USER,
        password=RDS_PASSWORD,
        database=RDS_DB
    )
    return conn