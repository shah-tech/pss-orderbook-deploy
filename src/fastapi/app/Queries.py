"""
This file contains general querries that do not modify the Redis Cache of the app

"""
from time_it import time_def
from sqlalchemy import create_engine, text

from app.SQLsetup import mysql_conn_str
import pandas as pd

@time_def(log_name="profiler")
def stock_list(limit: int = 10, skip: int = 0, term: str = "") -> pd.DataFrame:

    query = text(f"""SELECT symbol, price FROM orderbook.Product
    WHERE symbol NOT LIKE '%\.%' AND symbol NOT LIKE '%1%'
    AND symbol LIKE '{term}%'
    ORDER BY symbol
    LIMIT {limit} OFFSET {skip}
    ;
    """)

    sqlEngine = create_engine(mysql_conn_str())

    dbConnection = sqlEngine.connect()

    df = pd.read_sql(query, dbConnection);

    return df

@time_def(log_name="profiler")
def stock_quote(symbol: str = None) -> float:
    query = text(f"""SELECT price FROM orderbook.Product
                WHERE symbol='{symbol}'""")
    sqlEngine = create_engine(mysql_conn_str())

    dbConnection = sqlEngine.connect()

    df = pd.read_sql(query, dbConnection);

    return round(float(df['price']),2)

@time_def(log_name="profiler")
def num_stocks(term: str = "") -> int:
    query = text(f"""SELECT COUNT(*) as number FROM orderbook.Product
    WHERE symbol NOT LIKE '%\.%' AND symbol NOT LIKE '%1%'
    AND symbol LIKE '{term}%'
    """)

    sqlEngine = create_engine(mysql_conn_str())

    dbConnection = sqlEngine.connect()

    df = pd.read_sql(query, dbConnection);

    return int(df['number'])

