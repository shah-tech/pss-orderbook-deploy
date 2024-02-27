# general imports
from fastapi import FastAPI, Response, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import asyncio
import json
import time

from fastapi.responses import JSONResponse

# import sqlalchemy errors
from sqlalchemy import exc


# setup logging
import logging
from app.log import set_loggers
from app.fix import Fix
set_loggers()
fix = Fix()
fix.login()
logger = logging.getLogger('general')
http_logger = logging.getLogger('http')

# Redis DB cache
import redis
cache = redis.Redis(host='orderbookcache', port=6379)

# init fast api
app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# end fast api configs

# setup complete flag
setup_complete = False

# custom middleware
@app.middleware("http")
async def do_heartbeat_and_loki(request: Request, call_next):
    global setup_complete
    start_time = time.time()
    logger.debug(request.__dict__)
    path = request.scope['path']

    if not setup_complete:
        await startup_event()
        setup_complete = True
        
    try:
        response = await call_next(request)
        fix.heartbeat()
        process_time = round(time.time() - start_time, 8)
        http_logger.info(json.dumps({"time":process_time, "path":path}),
                     extra={"tags":{ "type":"request-info", "path-request":path}}
        )
        return response
    except exc.SQLAlchemyError as sqle:
        logger.info("DB ERROR: Trying to create again....")
        await startup_event()
        setup_complete = True
        return JSONResponse(status_code=500)
        

# Import modules created for this app
from app.PostClasses import PostUser, PostTrade, UserSession, UserOrder, UserOrdersReadRequest, UpdateRoles

from app.refresh import refresh_stock_list, stock_list_to_db

from app.session import new_user, authorize, authenticate, uname_from_sessionid, log_out, sessionid_from_uname, all_accounts, update_all_roles

from app.Queries import num_stocks, stock_quote, stock_list

from app.SQLsetup import create_tables, create_admin,create_roles,upsert_stock_data, get_roles, wait_mysql, load_product_from_backup

from app.Trade import new_order, get_orders_paged, cancel_order, get_holdings, num_orders

instrumentator = Instrumentator().instrument(app)

# App endpoints
@app.on_event("startup")
async def startup_event():
    instrumentator.expose(app) # connect to prometheus
    wait_mysql()
    create_tables()
    try:
         # create_roles will throw error if DB is already setup
        roles = create_roles()
        create_admin(roles['admin'])
    
        load_product_from_backup("Product2")
        # stock_list_to_db() # this made an API call, which may not be needed for our simple app....
    except:
        logger.info("Data Already Present..")


@app.post("/joinSite")
async def do_join(response: Response,
                user: PostUser
                ) -> dict:
    roles = get_roles()
    if new_user(user.uname, user.password, roles['user']):
        return {'new_user':"true"}
    else:
        return {'new_user':"false"}

@app.post("/update_roles")
async def update_roles(
            user_roles :UpdateRoles
                ) -> dict:

    if not authorize(user_roles.uname, user_roles.sessionid, ['admin'] ): return {"msg":"not authorized"}

    update_all_roles(user_roles.roles)

    return {"msg":"roles updated"}


@app.post("/new_feature")
async def new_feature() -> dict:
    return {"msg":"new_feature yay"}
        

@app.post("/trade")
async def do_trade(response: Response,
                trade: PostTrade
                ) -> dict:

    if not authorize(trade.uname, trade.sessionid ): return {"msg":"not authorized"}

    new_order(trade.uname, trade.symbol, trade.shares)

    return {"shares":trade.shares, "symbol":trade.symbol, "uname":trade.uname}

@app.post("/logout")
async def logout(session:UserSession) -> dict:

    if not authorize(session.uname, session.sessionid ): return {"msg":"not authorized"}

    print(f"deleting session {session.sessionid}")

    log_out(session.sessionid, session.uname)

    return {"sessionid":""}

@app.post("/holdings")
async def holdings(session : UserSession) -> list[dict]:

    if not authorize(session.uname, session.sessionid ): return [{"msg":"not authorized"}]

    return get_holdings(session.uname)

@app.post("/all_accounts")
async def accounts(session : UserSession) -> list[dict]:

    if not authorize(session.uname, session.sessionid, ["admin"]): return [{"msg":"not authorized"}]

    return all_accounts()

# feel like renaming to filer_orders....
@app.post("/all_orders")
async def orders(ordersRequest : UserOrdersReadRequest) -> list[dict]:

    if not authorize(ordersRequest.uname, ordersRequest.sessionid ): return [{"msg":"not authorized"}]

    otype = ordersRequest.otype.split(',')

    # user_orders_flag - orders for user only?
    uname = None if ordersRequest.user_orders_flag == 0 else ordersRequest.uname

    return {"orders":get_orders_paged(ordersRequest.page,
                            ordersRequest.results,
                            uname,
                            otype,
                            ordersRequest.symbol,
                            ordersRequest.orderby),
            "count":num_orders(uname,
                              otype,
                              ordersRequest.symbol)
    }

@app.post("/cancelorder")
async def orders(order : UserOrder) -> dict:

    if not authorize(order.uname, order.sessionid ): return [{"msg":"not authorized"}]

    cancel_order(order.orderid)

    return {}

@app.post("/login")
async def do_login(response: Response,
                user: PostUser
                ) -> dict:

    user = authenticate(user.uname, user.password)

    if user is None: return {"sessionid":""} # auth failed...

    return {    "sessionid": sessionid_from_uname(user.uname),
                "uname": user.uname,
                "role" : user.role[0].name
    }

@app.post("/active_users")
async def do_active_user(
    response: Response,
    session: UserSession):

    if not authorize(session.uname, session.sessionid, ["admin"]): 
        return [{"msg":"not authorized"}]

    users = []
    keys = cache.keys() # get all keys
    for k in keys:
        k = k.decode('utf-8') # make bytes into string
        # the keys with usernames look like "admin-sessionid"
        if "-sessionid" in k: 
            users.append(k.replace("-sessionid", "")) # append only the username

    return { "active-users" : users }
    

# should be made to post to verify login
@app.get("/stock_quote")
async def read_quote(
            response: Response,
            symbol: str = None ) -> dict:
    return {
            "quote":stock_quote(symbol),
            "symbol":symbol
    }

# should be made to post to verify login
@app.get("/number_of_stocks")
async def read_num_stocks(
            response: Response,
            term: str = "" ) -> dict:
    return {"number_of_stocks":num_stocks(term)}


# should be made to post to verify auth
@app.get("/stocklist")
async def read_tradeable(
            response: Response,
            symbols: list = None,
            limit: int = 10,
            skip: int = 0,
            term: str = "") -> list[dict] :

    #asyncio.create_task(refresh_stock_list(60*60*24)) # no need to refresh stock limit if not using API...
    symbols = stock_list(limit, skip, term).to_dict('records')

    return [ {"name": symbol["symbol"], "price": symbol['price'] } for symbol in symbols ]

