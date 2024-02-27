from sqlalchemy import select, delete, and_, or_, func
from sqlalchemy.orm import Session
from app.SQLsetup import mysql_conn_str
from app.SQLClasses import *
from sqlalchemy.dialects.postgresql import insert
from app.fix import Fix
import logging
from time_it import time_def

logger = logging.getLogger('general')
fix = Fix()

@time_def(log_name="profiler")
def num_orders(uname: str = None,
               otype: list = [],
               symbol: str = None) -> list[dict]:
    """
    @params:
    - otpye: can contain any of "pending", "partial_fill", "filled", "canceled", "canceled_partial_fill", "all"
    """

    session = Session(create_engine(mysql_conn_str()).connect())

    symbol = "%" if symbol is None or symbol == "" else symbol+"%"

    user = None if uname is None or uname == "" else \
        session.execute(select(User).where(User.uname == uname)).fetchone()[0]

    and_conditions = [True] # needs at least one condition
    or_conditions = [False]

    if user is not None: # is username is set, add that condition
        and_conditions.append(Order.userid == user.userid)

    if "pending" in otype:
        or_conditions.append(Order.status=="pending")

    if "partial_fill" in otype:
        or_conditions.append(Order.status=="partial_fill")

    if "canceled" in otype:
        or_conditions.append(Order.status=="canceled")

    if "canceled_partial_fill" in otype:
        or_conditions.append(Order.status=="canceled_partial_fill")

    if "filled" in otype:
        or_conditions.append(Order.status=="filled")

    if "all" in otype:
        or_conditions.append(True)

    and_conditions.append(Order.symbol.like(symbol))

    and_condition = and_(*and_conditions, or_(*or_conditions))

    result = [] # in case no results

    # return count of query
    return session.query(Order).filter(
        and_condition
    ).count()

@time_def(log_name="profiler")
def get_holdings(uname):
    session = Session(create_engine(mysql_conn_str()).connect())
    user = session.execute(select(User).where(User.uname == uname)).fetchone()[0]

    symbols = session.query(Fill.symbol).distinct().filter(Fill.userid==user.userid)

    holdings = []
    for symbol in symbols:
        symbol = symbol.symbol
        holding = {}

        value = session.query(func.sum(Fill.share*Fill.price)).filter(
            and_(Fill.userid == user.userid, Fill.symbol==symbol) )[0][0]

        shares = session.query(func.sum(Fill.share)).filter(
            and_(Fill.userid == user.userid, Fill.symbol==symbol) )[0][0]

        holding['symbol']=symbol
        holding['shares']=-shares
        holding['avg_price'] = 0 if shares == 0 else value / shares
        holdings.append(holding)

    return holdings

@time_def(log_name="profiler")
def get_orders_paged(page: int = 1,
               results: int = 10,
               uname: str = None,
               otype: list = [],
               symbol: str = None,
               order_c: str = None) -> list[dict]:
    """
    This functions gets orders starting at @page, for @results number of results
    It can include a @uname, or get all users orders. @otype specefies the order type.
    @symbol will search for any string in symbol with 'like "@symbol%"'
        - do not include % in argument, it is prepended in this function

    @params:
    - otpye: can contain any of "pending", "partial_fill", "filled", "canceled", "canceled_partial_fill", "all"
    """

    session = Session(create_engine(mysql_conn_str()).connect())

    symbol = "%" if symbol is None or symbol == "" else symbol+"%"

    user = None if uname is None or uname == "" else \
        session.execute(select(User).where(User.uname == uname)).fetchone()[0]

    and_conditions = [True] # needs at least one condition
    or_conditions = [False]

    if user is not None: # is username is set, add that condition
        and_conditions.append(Order.userid == user.userid)

    if "pending" in otype:
        or_conditions.append(Order.status=="pending")

    if "partial_fill" in otype:
        or_conditions.append(Order.status=="partial_fill")

    if "canceled" in otype:
        or_conditions.append(Order.status=="canceled")

    if "canceled_partial_fill" in otype:
        or_conditions.append(Order.status=="canceled_partial_fill")

    if "filled" in otype:
        or_conditions.append(Order.status=="filled")

    if "all" in otype:
        or_conditions.append(True)

    and_conditions.append(Order.symbol.like(symbol))

    and_condition = and_(*and_conditions, or_(*or_conditions))

    result = [] # in case no results

    if order_c == "date":
        order = Order.orderTime.desc()
    elif order_c == "amount":
        from sqlalchemy import desc
        order = desc(Order.shares * Order.price)
    # send query
    result= session.query(Order).filter(
        and_condition
    ).order_by(order).limit(results).offset((page-1)*results)

    orders = []
    for row in result:
        #row = row[0]
        order = {}
        order['symbol'] = row.symbol
        order['shares'] = row.shares
        order['price'] = row.price
        order['orderTime'] = row.orderTime
        order['orderid'] = row.orderid
        order['status'] = row.status
        order['uname'] = row.user.uname
        orders.append(order)
    return orders

@time_def(log_name="profiler")
def cancel_order(orderid: str=None) -> bool:

    session = Session(create_engine(mysql_conn_str()).connect())
    order = session.execute(select(Order).where(Order.orderid == orderid)).fetchone()[0]
    if order.status == "filled":
        return False
    if order.status == "partial_fill":
        order.status="canceled_partial_fill"
    else:
        order.status="canceled"

    qty_filled = -sum(f.share for f in order.fill)
    qty_remaining = order.shares - qty_filled

    logger.info(f"CANCEL ORDERID {order.orderid}")

    fix.cancel_order(qty_remaining=qty_remaining, stock = order.symbol,
               order_id = order.orderid, side=order.side, qty=order.shares, cum_qty=qty_filled)

    session.add(order)
    session.flush()
    session.commit()
    return True

@time_def(log_name="profiler")
def new_order(uname: str = None,
              symbol: str = None,
              shares: str = None,
) -> bool:

    session = Session(create_engine(mysql_conn_str()).connect())

    user = session.execute(select(User).where(User.uname == uname)).fetchone()[0]

    product = session.execute(select(Product).where(Product.symbol == symbol)).fetchone()[0]

    side = 1 if shares >=1 else 2 # 2 is sell...

    order = Order(userid=user.userid,
                  symbol=symbol,
                  shares=shares,
                  price=product.price,
                  side=side
    )
    session.add(order)
    session.flush()
    logger.info(f"New Orderid {order.orderid}")
    session.commit()
    try_fill_order(order.orderid)

@time_def(log_name="profiler")
def try_fill_order(orderid) -> bool:

    conn = create_engine(mysql_conn_str()).connect()

    session = Session(conn)

    order = session.execute(select(Order).where(Order.orderid == orderid)).fetchone()[0]

    fix.new_order(stock=order.symbol, qty= order.shares, price=order.price)

    order_options = session.execute(select(Order).where(
        and_(
            Order.symbol == order.symbol,
            Order.side != order.side,
            or_(Order.status == "pending" , Order.status == "partial_fill"),
            Order.price == order.price,
            Order.userid != order.userid
        )
      )
    )

    shares = order.shares

    logger.info(f"Finding matching orders for order id {order.orderid}")
    for order_option in order_options:
        o = order_option[0] # the order that may be matched...
        o_fills = sum([f.share for f in o.fill]) # count how many shares been filled
        o_shares = o.shares + o_fills # number of outstanding shares for that order...
        logger.info (f"Attempting to match order id {o.orderid}")
        if o_shares == shares*-1: # if we match all shares remaning!
            o.status = "filled"
            order.status = "filled"
            o_fill = Fill(share=o_shares*-1, orderid=o.orderid,
                          price=o.price, symbol=o.symbol, userid=o.userid ) # fill order found
            o.fill.append(o_fill)
            order_fill = Fill(share=o_shares, orderid=order.orderid,
                              price=order.price, symbol=order.symbol, userid=order.userid) # fill original order
            order.fill.append(order_fill)
            logger.info("TOTAL FILL FOR BOTH ORDERS")
            fix.full_fill(stock=order.symbol, order_id=order.orderid,
                          price=order.price, side=order.side, qty=order.shares)

            fix.full_fill(stock=o.symbol, order_id=o.orderid,
                          price=o.price, side=o.side, qty=o.shares)

            fills = -sum([f.share for f in o.fill]) # total shares filled
            session.add(o)
            break
        elif (shares < 0 and o_shares > shares*-1) or\
            (shares > 0 and o_shares < shares*-1):
            o.status = "partial_fill"
            order.status='filled'
            o_fill = Fill(share=shares, price=o.price, symbol=o.symbol, userid=o.userid) # orderid can be ommitted, orm will fill it in
            o.fill.append(o_fill)
            order_fill = Fill(share=shares*-1, price=order.price, symbol=order.symbol, userid=order.userid )
            order.fill.append(order_fill)
            logger.info("FILL CURRENT ORDER PARTIAL FILL EXISTING")
            fills = -sum([f.share for f in o.fill]) # total shares filled
            fix.partial_fill(stock=o.symbol, order_id=o.orderid, price=o.price,
                             side=o.side, qty=o.shares, last_order_qty=o_shares, cum_qty=fills)
            fix.full_fill(stock=order.symbol, order_id=order.orderid,
                          price=order.price, side=order.side, qty=order.shares)

            session.add(o)
            break
        elif (shares < 0 and o_shares > 0) or\
             (shares > 0 and o_shares < 0):  # partial fill
            o.status="filled"
            order.status ="partial_fill"
            o_fill = Fill(share=o_shares*-1, price=o.price, symbol=o.symbol, userid=o.userid)
            o.fill.append(o_fill)
            order_fill= Fill(share=o_shares, price=order.price, symbol=order.symbol, userid=order.userid)
            order.fill.append(order_fill)
            shares = shares + o_shares
            logger.info("PARTIAL FILL CURRENT ORDER FULL FILL EXISTING")
            fills = -sum([f.share for f in o.fill]) # total shares filled

            order_fills = -sum([f.share for f in order.fill]) # total shares filled
            fix.partial_fill(stock=order.symbol, order_id=order.orderid, price=order.price,
                              side=order.side, qty=order.shares, last_order_qty=o_shares, cum_qty=order_fills)
            fix.full_fill(stock=o.symbol, order_id=o.orderid,
                          price=o.price, side=o.side, qty=o.shares)

            session.add(o)

    #session.add(order)
    fills = -sum([f.share for f in order.fill]) # total shares filled

    session.add(order)
    session.flush()
    session.commit()







