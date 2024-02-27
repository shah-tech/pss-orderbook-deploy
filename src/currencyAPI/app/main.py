from fastapi import FastAPI, HTTPException, Query, Form
import requests
import re
from typing import Dict
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, String, DateTime, Numeric, update, MetaData, insert, select
from sqlalchemy.orm import sessionmaker

app = FastAPI()
 
API_BASE_URL = "https://api.exchangerate-api.com/v4/latest/"
COINBASE_URL = "https://api.coinbase.com/v2/"
 
async def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    response = requests.get(f"{API_BASE_URL}{from_currency.upper()}")
    if response.status_code == 200:
        data = response.json()
        if to_currency.upper() in data["rates"]:
            return data["rates"][to_currency.upper()]
        else:
            raise HTTPException(status_code=400, detail="To currency not supported")
    else:
        raise HTTPException(status_code=400, detail="From currency not supported")
 
 
@app.get("/exchange_rate")
async def exchange_rate(from_currency: str, to_currency: str) -> dict:
    rate = await get_exchange_rate(from_currency, to_currency)
    return {
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "exchange_rate": rate,
    }
 
 
@app.get("/convert_amount")
async def convert_amount(from_currency: str, to_currency: str, amount: float) -> dict:
    rate = await get_exchange_rate(from_currency, to_currency)
    converted_amount = amount * rate
    return {
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "amount": amount,
        "converted_amount": converted_amount,
    }
 
# @CODE : AN ENDPOINT THAT TAKES A STRING AND CONFIRMS IT HAS
# AT LEAST ONE UPPERCASE LETTER, ONE LOWERCASE LETTER, ONE NUMBER, AND IS 8 OR MORE CHARACTERS
# Make sure the return type matches the function signature, FastAPI enforces that it does!
@app.get("/check_password_strength")
async def check_password_strength(password: str) -> bool:
    uppercase_regex = re.compile(r'[A-Z]')
    lowercase_regex = re.compile(r'[a-z]')
    digit_regex = re.compile(r'\d')
 
    if (uppercase_regex.search(password) and
        lowercase_regex.search(password) and
        digit_regex.search(password) and
        len(password) >= 8):
        return True
    else:
        raise HTTPException(status_code=400, detail="Password does not meet the criteria.")
#    """
#    Coded By: <Roshni>  
#    This function checks whether a given password is strong enough, i.e., it contains at least one digit,
#    one lowercase letter, one uppercase letter, and is 8 characters long.
#    """
 
 
# @CODE : ADD ENDPOINT TO LIST ALL AVAILABLE CURRENCIES  
# NOTE : FastAPI enforces that the return type of the function matches the function signature!  
#        This is a common error!
 
@app.get("/available_currencies")
async def available_currencies(from_currency: str) -> dict:
    response = requests.get(f"{API_BASE_URL}{from_currency.upper()}")
    if response.status_code == 200:
        data = response.json()
        currency_codes = list(data['rates'].keys())    
        currency_codes.remove(from_currency.upper())
        c = {"Available Currencies " : currency_codes}
        return c
    else:
        raise HTTPException(status_code=400, detail="From currency not supported")
 
#    """
#    Coded by: Hamzah  
#    This endpoint returns a list of available fiat currencies that can be paired with the @from_currency parameter.  
#    @from_currency : str - you must specify a currency to see what currencies it can be compared against.
#    """
 

# @CODE : ADD ENDPOINT TO GET LIST OF CRYPTO CURRENCIES
# You can use this API https://docs.cloud.coinbase.com/sign-in-with-coinbase/docs/api-currencies
# Search for the endpoint that returns all the crypto currencies.
# Define route to get list of cryptocurrencies
@app.get("/available_crypto")
async def available_crypto() -> dict:
    # Make a request to the Coinbase API to retrieve cryptocurrency data
    crypto_data = (requests.get("https://api.coinbase.com/v2/currencies/crypto")).json()
    
    # Initialize an empty dictionary to store cryptocurrency codes and names
    cryptos = {}
    
    # Iterate through the cryptocurrency data and extract codes and names
    for crypto in crypto_data['data']:
        cryptos[crypto['code']] = crypto['name']
    
    # Return the dictionary containing cryptocurrency codes and names
    return cryptos
"""
Coded by: Shahjan
This endpoint allows you to see what cryptocurrencies are available.
"""

   
# @CODE : ADD ENDPOINT TO GET Price of crypto  
# Use the coinbase API from above

@app.get("/convert_crypto")
async def convert_crypto(from_crypto: str, to_currency: str) -> dict:
    # Convert input strings to uppercase for consistency
    from_crypto = from_crypto.upper()
    to_currency = to_currency.upper()
    
    # Make a request to the Coinbase API to get exchange rates
    response = requests.get(f"https://api.coinbase.com/v2/exchange-rates?currency={from_crypto}")
    
    # Check if the API request was successful
    if response.status_code == 200:
        # Parse the JSON response
        prdata = response.json()
        # Extract exchange rates for the specified cryptocurrency
        rates = prdata["data"]["rates"].get(to_currency)
        
        # Check if the conversion rate is available
        if rates is not None:
            # Return the conversion rate along with the input parameters
            return {"from_crypto": from_crypto, "to_currency": to_currency, "conversion_rate": rates}
        else:
            # Raise an HTTPException if the currency conversion is not available
            raise HTTPException(status_code=400, detail="Currency conversion not available for the specified currency")
    else:
        # Raise an HTTPException if the API request failed
        raise HTTPException(status_code=400, detail="Failed to retrieve data from Coinbase API")

"""
Coded by: Shahjan
This endpoint allows you to get a quote for a cryptocurrency in any supported currency.
@from_crypto - choose a cryptocurrency (e.g., BTC or ETH)
@to_currency - choose a currency to obtain the price in (e.g., USD or CAD)
"""


# @CODE : ADD ENDPOINT TO UPDATE PRICE OF ASSET IN ORDERBOOK DB
# The code below starts you off using SQLAlchemy ORM
# Dependencies should already be installed from your requirements.txt file
# Using the ORM instead of raw SQL is safer and less coupled: it is best practice!
@app.get("/update_orderbookdb_asset_price")
async def update_orderbookdb_asset_price(symbol: str, new_price: float) -> dict:
    """
    Coded by: Karan  
    This endpoint allows us to update the price of the assets in the app  
    @symbol - pick a symbol to update the price of in the orderbook app  
    @new_price - The new price of the symbol  
    """

    # import sqlalchemy
    from sqlalchemy import create_engine, Table, Column, String, DateTime, Numeric, update, MetaData
    from sqlalchemy.orm import sessionmaker

    # create an engine for building sessions
    engine = create_engine('mysql+pymysql://wiley:wiley123@af09504f917d345ada65a1ed6e73297a-1421861172.us-east-1.elb.amazonaws.com/orderbook')

    # create an ORM object that maps to the Product table
    metadata = MetaData()
    product_table = Table('Product', metadata,
        Column('symbol', String(16), primary_key=True),
        Column('price', Numeric(precision=15, scale=2)),
        Column('productType', String(12)),
        Column('name', String(128)),
        Column('lastUpdate', DateTime)
    )
    metadata.create_all(engine)

    # create a database session maker
    Session = sessionmaker(bind=engine)

    try:
        # Instantiate the session
        session = Session()
        # create the statement to udpate
        stmt = update(product_table).where(product_table.c.symbol == symbol).values(price=new_price)
        # execute commit and flush the statement
        session.execute(stmt)
        session.commit()
        session.flush()
        return {"update_report": "success", "symbol": symbol, "new_price": new_price}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="An error occurred, make sure symbol exists and price is numeric")
    finally:
        session.close()


# @CODE : ADD ENDPOINT FOR INSERTING A CRYPTO CURRENCY INTO THE ORDERBOOK APP
# HINT: Make use of the convert_crypto function from above! 
#       You will need to use the await keyword to wait for the result (otherwise it will run async and not wait for the result)
@app.get("/add_crypto_to_orderbook")
async def add_crypto_to_orderbook(symbol: str) -> dict:
 
    #call convert_crypto function
    result = await convert_crypto(symbol, "USD")  # change "USD" to the desired currency
        
    # only accept alphabetical characters
    if not symbol.isalpha():
        raise HTTPException(status_code=400, detail="Invalid input. Only alphabetical characters are accepted.")
    
    # create an engine for building sessions
    engine = create_engine('mysql+pymysql://wiley:wiley123@af09504f917d345ada65a1ed6e73297a-1421861172.us-east-1.elb.amazonaws.com/orderbook')

    # create an ORM object that maps to the Product table
    metadata = MetaData()
    product_table = Table('Product', metadata,
        Column('symbol', String(16), primary_key=True),
        Column('price', Numeric(precision=15, scale=2)),
        Column('productType', String(12)),
        Column('name', String(128)),
        Column('lastUpdate', DateTime)
    )
    metadata.create_all(engine)

    # create a database session maker
    Session = sessionmaker(bind=engine)

    try:
        # instantiate the session
        session = Session()
        # statement to insert a new record 
        stmt = insert(product_table).values(
                symbol=symbol, 
                price=result['price'])
        # execute statement, commit and flush
        session.execute(stmt)
        session.commit()
        session.flush()
        return {"insert_report": "success", "symbol": symbol, "price": result['price']}
        #exception
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Server error occured : selected currency is already stored in the database!")
        #close session
    finally:
        session.close()

