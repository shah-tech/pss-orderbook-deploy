import { useParams } from "react-router-dom";
import { useState, useEffect  } from 'react'
import NumberPicker from "react-widgets/NumberPicker";
import classes from './OrderList.module.css';

import AuthContext from '../store/auth-context'
import { useContext } from 'react';

const Trade = () => {


    const params = useParams()
    const [price, setPrice] = useState()
    const [type, setType] = useState(params.type)
    const [shares, setShares] = useState(params.type=="buy" ? 1 : -1)
    const [symbol, setSymbol] = useState(params.symbol)

    const authContext = useContext(AuthContext)


    const placeOrderHandle = () =>{

        const uname = authContext.uname;
        const sessionid = authContext.sessionid;

        fetch('http://localhost:8000/trade', {
            method: 'post',
            headers: {'Content-Type': "application/json; charset=utf-8"},
            body: JSON.stringify({
                'uname': uname,
                'symbol': symbol,
                'shares' : shares,
                'sessionid' : sessionid
            }),
        }).then((res) => {
            return res.json()
        }).then((data) => {

            alert("order placed! View in portfolio page")
        });
    }


   function fetchStockPrice(symbol){ // add session id to this call
        fetch('http://localhost:8000/stock_quote?symbol='+symbol).then(response => {
          return response.json();
        }).then(data => {
            setPrice(data.quote);
        }).catch();
      }

    useEffect(() => {
        fetchStockPrice(symbol)
    }, [symbol]);

    const numPickHandler = (val) => {
        if (shares == 1 && val == 0){
            setShares(-1)
            setType("sell")
        }else if (shares == -1 && val == 0){
            setShares(1)
            setType("buy")
        }else{
            setShares(val)
        }
    }



    return(
        <section>
        <h1>{type} order</h1>
        <h2>Symbol: {params.symbol}</h2>
        <h3>${price}</h3>
          <NumberPicker
                skip={1}
                value={shares}
                onChange={numPickHandler}
                min={-100000}
                max={100000}
          />
        <button type='button' onClick={placeOrderHandle} className={classes.lgBtn}>Place Order</button>

        </section>
    );
};


export default Trade;
