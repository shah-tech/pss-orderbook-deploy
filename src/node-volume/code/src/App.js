import { Link, Routes,  Route,  BrowserRouter  } from "react-router-dom";
import Quotes from './components/Quotes';
import LoginForm from './components/LoginForm';
import Trade from './components/Trade';
import Orderbook from './components/Orderbook';
import Holdings from './components/Holdings';
import Navigation from './components/Navigation';
import Manage from './components/Manage';
import './App.css';
import AuthContext from './store/auth-context'
import { useContext } from 'react';

function App() {

  const authContext = useContext(AuthContext)
  const isLoggedIn = authContext.isLoggedIn;
  const role = authContext.role;

    return (
    <BrowserRouter>
      <Navigation />
      <Routes>
        <Route path="/" element={
            <section>
            <h1>Brokerage App</h1>
            </section>
        }/>
        <Route path="/quotes" element={
            isLoggedIn && <Quotes />
        } />
        <Route path='/Login' element={
            <LoginForm />
        } />
        <Route path='/Trade/:type/:symbol' element={
            isLoggedIn && <Trade />
        } />
         <Route path='/portfolio' element={
            isLoggedIn && (<> <Orderbook />  <Holdings /> </>)
        } />
        <Route path='/orderbook' element={
            isLoggedIn && <Orderbook />
        } />
        <Route path='/manage' element={
            isLoggedIn && role == "admin" && <Manage />
        } />



      </Routes>
    </BrowserRouter>

  );
}

export default App;
