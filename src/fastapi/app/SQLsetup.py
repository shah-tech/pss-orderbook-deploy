import os
import pandas as pd
from app.SQLClasses import *
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from datetime import datetime
import logging






logger = logging.getLogger('general')

def mysql_conn_str(
    uname="wiley",
    password="wiley123", # should use env variables or docker secrets....
    host="orderbookdb",
    db="orderbook"
):
    """
    desc:
    ----
    builds and returns a pymysql connection string

    """
    # urlib.parse required in password contains special characters, like @...
    import urllib.parse
    password = urllib.parse.quote_plus(password)

    return f"mysql+pymysql://{uname}:{password}@{host}/{db}"

def hash_password(password: str=None) ->str:
    
    import hashlib

    # Create an MD5 hash object... is MD5 collision resistant? 
    hash_object = hashlib.md5(password.encode())

    # Get the hash value
    hash_value = hash_object.hexdigest()
    
    return hash_value

def create_tables() -> None:
    Base.metadata.create_all(create_engine(mysql_conn_str()))

def create_admin(admin_role: Role = None) -> None:
    session = Session(create_engine(mysql_conn_str()).connect())

    user1 = User(uname="admin", password=hash_password("admin"))
    user1.role.append(admin_role)

    user2 = User(uname="wiley", password=hash_password("wiley"))
    user2.role.append(admin_role)

    session.add(user1)
    session.add(user2)
    session.flush()


    session.commit()

def site_roles() -> list:
    return [
        "admin",
        "it",
        "user"
    ]

def create_roles() -> dict:

    session = Session(create_engine(mysql_conn_str()).connect())

    roles = site_roles()

    roles_dict = {role: Role(name=role) for role in roles}

    session.add_all(
        roles_dict.values()
    )

    session.commit()

    return roles_dict

def get_roles() ->dict:

    session = Session(create_engine(mysql_conn_str()).connect())

    results = session.execute(select(Role))

    roles_dict = {}

    for result in results:
        role = result[0]
        roles_dict[role.name] = role
    session.close()
    return roles_dict



def upsert_stock_data(df: pd.DataFrame = None ) -> None:
    """
    df can be list of dicts or dataframe

    symbol = Column(String(16), primary_key=True)
    price = Column(DECIMAL(15,2))
    productType = Column(String(12))
    name = Column(String(128))
    lastUpdate= Column(DateTime)
"""

    df = df if df is not None else pd.DataFrame(stock_list_via_api())

    df = df if type(df) == pd.DataFrame else pd.DataFrame(df) # in case a list of dicts is passed

    df["lastUpdate"] = datetime.now()

    df.rename(columns={"type":"productType"}, inplace=True) # rename to match DB

    df = df[["symbol", "price", "productType", "name", "lastUpdate"]]

    logger.info('-----------  HEAD ---------')

    sqlEngine = create_engine(mysql_conn_str())

    dbConnection = sqlEngine.connect()

    session = Session(dbConnection)

    stmt = insert(Product).values(df.to_dict('records'))

    stmt.on_conflict_do_update(
        constraint="symbol",
        set_={"price": stmt.excluded.price, "lastUpdate": stmt.excluded.lastUpdate}
    )

    session.execute(stmt)
    session.commit()

def load_product_from_backup(backup_name):
    """
    backup_name - table name of financial product backups
    This function assumes a backup of Product table is present
    It was easier to do this than get SQLAlchemy ORM to work adding FK to existing table..
    """
    logger.info("inserting............")
    session = Session(create_engine(mysql_conn_str()).connect())
    session.execute(text(f"INSERT INTO Product SELECT * FROM {backup_name};").execution_options(autocommit=True))
    session.execute(text(f"DROP TABLE {backup_name};").execution_options(autocommit=True))
    session.commit()
    session.close()


def wait_mysql():
    import time
    while True:
        try:
            session = Session(create_engine(mysql_conn_str()).connect())
            session.close()
            break
        except:
            time.sleep(3)
            logger.info("waiting for db to connect...")

