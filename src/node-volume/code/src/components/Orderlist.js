import React from 'react';

import Order from './Order';
import classes from './OrderList.module.css';

const OrderList = (props) => {
  return (
    <ul className={classes['orders-list']}>
      {props.orders.map((order) => (
        <Order
          symbol={order.symbol}
          price={order.price}
          shares={order.shares}
          orderTime={order.orderTime}
          orderid={order.orderid}
          status={order.status} 
	  uname={order.uname} />
      )

      )}
    </ul>
  );
};

export default OrderList;
