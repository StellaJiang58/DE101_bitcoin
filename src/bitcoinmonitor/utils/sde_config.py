import os
from bitcoinmonitor.utils.db import DBConnection


# def get_warehouse_creds() -> DBConnection:
#     return DBConnection(
#         user=os.getenv('WAREHOUSE_USER', ''),
#         password=os.getenv('WAREHOUSE_PASSWORD', ''),
#         db=os.getenv('WAREHOUSE_DB', ''),
#         host=os.getenv('WAREHOUSE_HOST', ''),
#         port=int(os.getenv('WAREHOUSE_PORT', 5432)),
#     )
    
def get_warehouse_creds() -> DBConnection:
    return DBConnection(
        user='postgres',
        password='3006',
        db='postgres',
        host='127.0.0.1',
        port='5432',
    )
    
