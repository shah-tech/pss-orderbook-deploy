from pydantic import BaseModel
class PostUser(BaseModel): # model for login post request below
    uname: str = ""
    password: str = ""
    email: str = ""

class UserSession(BaseModel):
    sessionid: str = ""
    uname: str = ""

class UpdateRoles(UserSession):
    roles: dict = {}

class UserOrdersReadRequest(UserSession):
    user_orders_flag: int = 0
    page: int = 1
    results: int = 10
    otype: str = "all"
    symbol: str = ""
    orderby: str = "date"

class UserOrder(UserSession): # for modifying or canceling orders
    orderid: str = ""


class PostTrade(UserSession):
    shares: int = 0
    symbol: str = ""

