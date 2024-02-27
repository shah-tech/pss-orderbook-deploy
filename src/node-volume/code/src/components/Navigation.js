import { Link } from 'react-router-dom';

import classes from './Navigation.module.css'
import { useContext, useEffect, useState } from 'react';
import AuthContext from '../store/auth-context'
import {default as logo} from '../logo.svg'
import { useNavigate } from 'react-router-dom';

const Navigation = () => {

    const [wlyPrice, setWlyPrice] = useState([])
    const navigate = useNavigate();

    function fetchStockPrice(symbol){ // add session id to this call
        fetch('http://localhost:8000/stock_quote?symbol='+symbol).then(response => {
          return response.json();
        }).then(data => {
          setWlyPrice(data.quote);
        }).catch();
      }

    useEffect(() => {
        fetchStockPrice('wly')
    }, []);

    const authContext = useContext(AuthContext)
    const isLoggedIn = authContext.isLoggedIn;
    const sessionid = authContext.sessionid;
    const uname = authContext.uname;
    const role = authContext.role;

    function logOutHandler(e){
        e.preventDefault()
        authContext.logout()

         fetch('http://localhost:8000/logout', {
            method: 'post',
            headers: {'Content-Type': "application/json; charset=utf-8"},
            body: JSON.stringify({
                'sessionid' : sessionid,
                'uname' : uname
            }),
        }).then((res) => {
            return res.json()
        }).then((data) => {
            alert("logged out")
            //navigate('/')
        });
    }

    return (
        <header className={classes.header}>
        <Link to ="/">
            <div className={classes.logo}>
                <img src={logo} width="300" />

            </div>
        </Link>
        <span className={classes.info}>
            Wiley (WLY) ${wlyPrice}
        </span>
        <nav>
            <ul>

                <li><Link to="/">Home</Link></li>
                {isLoggedIn && (
                    <>
                    <li><Link to="/quotes">Quotes</Link></li>
                    <li><Link to="/portfolio">Portfolio</Link></li>
                    <li><Link to="/orderbook">Orderbook</Link></li>
                    </>
                )}
                {isLoggedIn && role == 'admin' && (
                    <li><Link to="/manage">Manage Accounts</Link></li>
                )}
                {isLoggedIn &&  (
                    <li><Link to="" onClick={logOutHandler}>Logout ({uname})</Link></li>
		)}
	        {!isLoggedIn && (
                    <li><Link to="/login">Login</Link></li>
                )}
 
            </ul>
        </nav>
    </header>
    );
};

export default Navigation;
