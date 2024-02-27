import pandas as pd

from app.SQLsetup import upsert_stock_data
from time_it import time_def

import time
from datetime import datetime

import redis

cache = redis.Redis(host='redis', port=6379)

#@time_def
def stock_list_to_db(df : pd.DataFrame = None) -> None:
    """
    df can be list of dicts or dataframe
    """
    upsert_stock_data(df) #This is with API..... Not sure if we need (or want) API for data feed... overkill?

    #stock_data_from_infile()

    timestamp = int(time.mktime(datetime.now().timetuple()))

    cache.set('stock_list_update_time', timestamp)


@time_def
async def refresh_stock_list(seconds_to_refresh: int = 30, ) -> bool:
    """
    desc:
    ----
    Function refreshes mysql stock list if the data was last refreshed
    longer than mins_to_refresh

    returns:
    -------
    True if refresh happened (first time running, or outside time limit)
    False if no refresh
    """


    if cache.get("stock_list_update_time") is None:
        timestamp = int(time.mktime(datetime.now().timetuple()))
        cache.set('stock_list_update_time', timestamp)

    if cache.get("stock_list_lock") is None:
        cache.set("stock_list_lock", 0)

    if int(cache.get("stock_list_lock")) == 1: return False # being updated...

    last = int(cache.get("stock_list_update_time"))

    last_timestamp = datetime.fromtimestamp(last)

    diff_seconds = (datetime.now() - last_timestamp).seconds

    if diff_seconds > seconds_to_refresh:
        cache.set("stock_list_lock", 1)
        stock_list_to_db()
        cache.set("stock_list_lock", 0)
        return True

    return False




