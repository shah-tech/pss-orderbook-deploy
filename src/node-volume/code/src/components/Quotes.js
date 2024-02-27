import React, { useState, useRef, useEffect, useContext } from 'react';


import NumberPicker from "react-widgets/NumberPicker";
import SymbolList from './SymbolList';
import classes from './OrderList.module.css';
import AuthContext from '../store/auth-context';

const Quotes = (props) => {
//  const authContext = useContext(AuthContext) get session id from here..

  const [symbols, setSymbols] = useState([]);
  const [skip, setSkip] = useState([0]);
  const [maxPage, setMaxPage] = useState([]);
  const [numStocks, setNumStocks] = useState([]);
  const [pageNum, setPageNum] = useState([1]);
  const [term, setTerm] = useState([])
  const itemsPerPage=10;

  function fetchStockListHandler(){ // add session id to this call
    fetch('http://localhost:8000/stocklist?skip='+skip+"&term="+term).then(response => {
      return response.json();
    }).then(data => {
      setSymbols(data);
    }).catch();
  }

    function fetchStockCount(){
     fetch('http://localhost:8000/number_of_stocks?term='+term).then(response => {
            return response.json();
        }).then(data => {
          const local_num_stocks = parseFloat(data.number_of_stocks) // because numStocks wont be updated right away
          setNumStocks(local_num_stocks)
          setMaxPage(Math.ceil(local_num_stocks/itemsPerPage))
      })
    }


  useEffect(() => { // run every time skip is updated
    fetchStockListHandler()
    fetchStockCount()
    setPageNum(Math.ceil(skip/itemsPerPage+1))
  }, [skip]);

    useEffect(() => {
        if (skip == 0){
            fetchStockListHandler()
            fetchStockCount()
        }else{
            setSkip(0)
        }

    }, [term])

    function firstPageHandler(){
        setSkip(0)
    }

    function lastPageHandler(){
        setSkip(numStocks-10)
    }

    function numPickHandler(value){
        setSkip((value-1)*10)
    }

    function onSearchHandler(e){
        setTerm(e.target.value)
    }

  return (
    <>
    <section>
      <span>Page number {pageNum} of {maxPage} </span>
      <NumberPicker
            skip={1}
            value={pageNum}
            onChange={numPickHandler}
            min={1}
            max={maxPage}
      /><br />
      <span>Search Symbols</span>
      <input type="text" name="search"
             onChange={onSearchHandler} />
    </section>
    <section>
        <span>
        <button className={classes.lgBtn} onClick={firstPageHandler}>First page</button>
        <button className={classes.lgBtn} onClick={lastPageHandler}>Last Page</button>
        </span>
        <SymbolList symbols={symbols} />
    </section>
    </>
  );
};

export default Quotes;
