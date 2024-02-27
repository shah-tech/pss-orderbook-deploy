import React, {useContext} from 'react';

import AuthContext from '../store/auth-context'

import { Link, useNavigate  } from 'react-router-dom';
import classes from './Order.module.css';

const Symbol = (props) => {

    const authContext = useContext(AuthContext)

    const cancel = () =>{
     fetch('http://localhost:8000/cancelorder', {
            method: 'post',
            headers: {'Content-Type': "application/json; charset=utf-8"},
            body: JSON.stringify({
                'orderid' : props.orderid,
                'uname'   : authContext.uname,
                'sessionid': authContext.sessionid
            }),
        }).then((res) => {
            return res.json()
        }).then((data) => {
            alert("order deleted")
            window.location.reload();
        });

    }

return (
    <li className={classes.order}>
      <h2>Symbol :{props.symbol}</h2>
      <h3>Price  :{props.price}</h3>
      <h3>Time  :{props.orderTime}</h3>
      { window.location.pathname == "/orderbook" && (<h3>User : {props.uname}</h3>) }
      <h4>Shares : {props.shares}</h4>
      <h4>Status : {props.status}</h4>
      { window.location.pathname != "/orderbook" &&
        (props.status != "filled" && !props.status.includes('cancel') )  && (
        <>
      <Link to="" onClick={cancel}>cancel order</Link>
          </>
      )}
    </li>
  );
};

export default Symbol;
