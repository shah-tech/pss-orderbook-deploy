import React from 'react';

import { Link  } from 'react-router-dom';
import classes from './Order.module.css';

const Symbol = (props) => {


return (
    <li className={classes.order}>
      <h2>{props.name}</h2>
      <h3>
          <Link className={classes.buy}
            to={"/Trade/buy/"+props.name}>buy</Link>
          {props.price}
          <Link className={classes.sell}
            to={"/Trade/sell/"+props.name}>sell</Link>
      </h3>
    </li>
  );
};

export default Symbol;
