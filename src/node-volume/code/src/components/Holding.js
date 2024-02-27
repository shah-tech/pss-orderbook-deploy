import React from 'react';

import { Link, useNavigate  } from 'react-router-dom';
import classes from './Order.module.css';

const Holding = (props) => {

    //const navigate = useNavigate()

return (
    <li className={classes.order}>
      <h2>Symbol :{props.symbol}</h2>
      <h3>Shares : {props.shares}</h3>
    </li>
  );
};

export default Holding;
