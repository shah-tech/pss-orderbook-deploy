import AuthContext from '../store/auth-context'
import HoldingList from './HoldingList.js'
import { useContext, useState, useEffect } from 'react';


const Holdings = () => {

    const authContext = useContext(AuthContext)
    const [holdings, setHoldings] = useState([])

    const getHoldings = () =>{
        const sessionid = authContext.sessionid;
        const uname = authContext.uname;

        fetch('http://localhost:8000/holdings', {
            method: 'post',
            headers: {'Content-Type': "application/json; charset=utf-8"},
            body: JSON.stringify({
                'sessionid' : sessionid,
                'uname' : uname
            }),
        }).then((res) => {
            return res.json()
        }).then((data) => {
            setHoldings(data)
        });
    }

    useEffect(() => { // run every time skip is updated
      getHoldings()
    }, []);




    return (
    <section>
        <h1>Holdings</h1>
        <HoldingList holdings={holdings} />
    </section>
    )
}

export default Holdings;
