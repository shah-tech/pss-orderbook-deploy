import AuthContext from '../store/auth-context'
import Orderlist from './Orderlist.js'
import { useContext, useState, useEffect } from 'react';
import axios from "axios";
import Pagination from "react-bootstrap/Pagination";
import Form from "react-bootstrap/Form";


const Orderbook = () => {

  let resultsPerPage = 5
  let greeting = "Order Book"
  let pagesToShow = 5 // num of pages before and after active
  let user_orders_only=0 // show all orders
  if (window.location.pathname != "/orderbook"){
     user_orders_only=1 // only show user orders
     resultsPerPage = 5 // show less results if not on orderbook page
     greeting = "Your Orders"
  }
  const authContext = useContext(AuthContext)
  const [active, setActive] = useState(1);
  const [orders, setOrders] = useState([]);
  const [type, setType] = useState('all');
  const [orderby, setOrderby] = useState('date');
  const [symbol, setSymbol] = useState('');
  const [numOfOrders, setNumOfOrders] = useState(0)
  const [numOfPages, setNumOfPages] = useState(1)

  const [pages, setPages] = useState([]);
  const totalOrders = []

  for (let i=0; i <= numOfOrders; i++){
    totalOrders.push(i);
  }

  const pagination = (i) => {
         setActive(i);
   }

  const get_orders_data = () =>{
                axios.post(
                     "http://localhost:8000/all_orders",
                     {
                         uname: authContext.uname,
                         sessionid: authContext.sessionid,
                         page: active,
                         results: resultsPerPage,
                         user_orders_flag:user_orders_only,
			 otype: type,
			 symbol:symbol,
			 orderby: orderby
                     }
                 ).then((response) => {
                    setOrders(response.data.orders)
		    let num_orders = response.data.count
		    setNumOfPages(Math.ceil(num_orders/resultsPerPage))
                    setNumOfOrders(num_orders)
                 }, (error) =>{
                     console.log(error)
                 })

  }

    useEffect(() =>{
         let tmp_pages = []
         let i = 1
         let add = 0
         let endAdd = 0
         let limit = 0
         if (active >= pagesToShow){
            add = active - pagesToShow
         }
         endAdd = add
         if (active < numOfPages){
            endAdd +=1
         }
        if (numOfPages <= pagesToShow){
            limit = numOfPages
        }else{
            limit = pagesToShow+endAdd
        }
          for (let i =1+add; i <= limit; i++){
              tmp_pages.push(
                  <Pagination.Item
                    key={i}
                    active={i === active}
                    onClick={()=>pagination(i)}
                  >
                    {i}
                  </Pagination.Item>
              );
          }
          setPages(tmp_pages)
    },[numOfPages, active])

  useEffect(() => {
	get_orders_data()
  }, [active])

     useEffect(
         () => {
		 if (active != 1){
          		setActive(1) 
		 }else{
		 	get_orders_data()
		 }
         }, [type, symbol, orderby]
     );

  return (
      <section>
        <div style={{display: "inline-block"}}>
	  <h2>{greeting}</h2>
	  
	<Form.Select
	  onChange={ 
		e => {
		  	setOrderby(e.target.value)
		}
	  }
	  >
        	<option value="date">Sort by Order Date</option>
        	<option value="amount">Sort by Order Amount</option>
      	</Form.Select>
	<br />
	<Form.Select
	  onChange={ 
		e => {
		  	setType(e.target.value)
		}
	  }
	  >
        	<option value="all">All Orders</option>
        	<option value="pending,partial_fill">All Pending Orders</option>
        	<option value="pending">Pending With No Fill</option>
        	<option value="partial_fill,filled">Filled or Partial Filled Orders</option>
        	<option value="filled">Filled </option>
        	<option value="partial_fill">Partially Filled Orders</option>
        	<option value="canceled,canceled_partial_fill">All Canceled Orders</option>
        	<option value="canceled_partial_fill">Canceled After Partial Fill</option>
        	<option value="canceled">Canceled With No Partial Fill</option>
      	</Form.Select>
	<br />
	<Form.Control type="text" placeholder="Filter on Symbol"
		onChange={
			e => {
                        	setSymbol(e.target.value)
                	}
		}
	  />
	<br />
        <Pagination size="sm">
            <Pagination.First
                onClick={() => {
                    pagination(1);
                }}
            />
            <Pagination.Prev
                onClick={() => {
                  if (active > 1) {
                    pagination(active - 1);
                  }
                }}
            />
            {pages}
            <Pagination.Next
                onClick={() => {
                  if (active < numOfPages ) {
                    pagination(active + 1);
                  }
                }}
            />
            <Pagination.Last
                onClick={() => {
                      pagination(numOfPages);
                }}
            />
        </Pagination>
       </div><br />
        <span>Total {numOfPages} pages, {numOfOrders} Orders</span>
        <Orderlist orders={orders} />
      </section>

  );

}

export default Orderbook;
