def mysql_conn_str(
    uname="wiley",
    password="wiley123", # should use env variables or docker secrets....
    host="mysql",
    db="FinancialMarketServicedb"
):
    """
    desc:
    ----
    builds and returns a pymtsql connection string

    """
    # urlib.parse required in password contains special characters, like @...
    import urllib.parse
    password = urllib.parse.quote_plus(password)

    return f"mysql+pymysql://{uname}:{password}@{host}/{db}"
