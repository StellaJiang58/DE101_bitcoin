import datetime
import logging 
import sys 
from typing import Any, Optional
import psycopg2.extras
import requests 
from bitcoinmonitor.utils.db import WarehouseConnection
from bitcoinmonitor.utils.sde_config import get_warehouse_creds
   


# * The code to pull data from CoinCap API and load it into our warehouse is at exchange_data_etl.py 
# 1. Extract data from CoinAPI 
def get_exchange_data():
    url = 'https://api.coincap.io/v2/exchanges'
    try:
        r = requests.get(url)
    except requests.ConnectionError as e:
        logging.error(f"There was an error with the request,{e}")
        sys.exit(1)
    return r.json().get('data',[])


# 2. Transfomr timestamp into UTC format 
def get_utc_from_unix_time(unix_tx: Optional[Any]):
    return (
        datetime.datetime.fromtimestamp(int(unix_tx) / 1000)
        if unix_tx
        else None
    )
   
# 3. Create schema for exchange data
   
def create_schecma(table_name):
    """
    Creates a PostgreSQL table schema with the given table name.
    
    Parameters:
        table_name (str): The name of the table to create.
    """
    sql = f'''
    DROP TABLE IF EXISTS {table_name};
    CREATE TABLE {table_name}
    (id VARCHAR(50),
    name VARCHAR(50),
    rank INT,
    percentTotalVolume NUMERIC(8, 5),
    volumeUsd NUMERIC(18, 5),
    tradingPairs INT,
    socket BOOLEAN,
    exchangeUrl VARCHAR(50),
    updated_unix_millis BIGINT,
    updated_utc TIMESTAMP); '''
    try:
        with WarehouseConnection(get_warehouse_creds()).managed_cursor() as curr:
            curr.execute(sql)
            print(f"Schema for table '{table_name}' created successfully.")
    except Exception as e:
        print(f"Error creating schema for table '{table_name}': {e}")
    
if __name__ == "__main__":
    create_schecma("exchange")
        
# 4. Insert data into exchange 
def get_exchange_insert_query():
    return '''
    INSERT INTO exchange (
        id,
        name,
        rank,
        percenttotalvolume,
        volumeusd,
        tradingpairs,
        socket,
        exchangeurl,
        updated_unix_millis,
        updated_utc
    )
    VALUES (
        %(exchangeId)s,
        %(name)s,
        %(rank)s,
        %(percentTotalVolume)s,
        %(volumeUsd)s,
        %(tradingPairs)s,
        %(socket)s,
        %(exchangeUrl)s,
        %(updated)s,
        %(update_dt)s
    );
    '''
        
# 5. Load data into Warehouse
def load_data_into_postgres():
    data = get_exchange_data()
    for d in data:
        d['update_dt'] = get_utc_from_unix_time(d.get('updated'))
    with WarehouseConnection(get_warehouse_creds()).managed_cursor() as curr:
        psycopg2.extras.execute_batch(curr, get_exchange_insert_query(), data)
        
        
if __name__ == '__main__':
    load_data_into_postgres()    
    
    