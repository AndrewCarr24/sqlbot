import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
from datetime import date
import boto3
import json
from cryptography.hazmat.primitives import serialization
from snowflake.snowpark import Session
from snowflake.snowpark.functions import *
import os
from pathlib import Path

class Connect:
    @property
    def session(self):
        return Session.builder.configs(self.connection_params).create()

    def __init__(self, config_file="snowflake-read.json"):
        self.ssm = boto3.client('ssm')
        with open(config_file) as f:
            self.connection_params = json.load(f)
        # pull out connection name to construct SSM path
        snowflake_connection_name = self.connection_params.pop('connectionName')
        remote_connection_params = json.loads(self.ssm.get_parameter(Name=snowflake_connection_name, WithDecryption=True)['Parameter']['Value'])
        # merge
        self.connection_params.update(remote_connection_params)

        encoded_private_key = self.connection_params['private_key']
        private_key = serialization.load_pem_private_key(
            encoded_private_key.encode(),
            password=None,
        )
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption())

        # add private key bytes
        self.connection_params['private_key'] = private_key_bytes
        print(f"Connected to Snowflake Env: {self.connection_params['account']} User: {self.connection_params['user']}")

def WriteDFtoSnowflake(pandas_df=None,table_name=None,database='MART',schema='ML_MODEL_OUTPUT'):
        conn= Connect(config_file="snowflake-write.json")
        session = conn.session
        session.sql(f"use {database}.{schema};").collect()
        session.write_pandas(pandas_df, table_name, database=database, schema=schema)
        print(f"Successfully loaded {len(pandas_df.index)} to table {database}.{schema}.{table_name}")