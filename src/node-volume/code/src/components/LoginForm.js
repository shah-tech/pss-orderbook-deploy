import { useState, useRef, useContext } from 'react';
import AuthContext, { AuthContextProvider  } from '../store/auth-context';
import { useNavigate } from 'react-router-dom';

//import classes from './AuthForm.module.css';

const LoginForm = () => {
  const [isLogin, setIsLogin] = useState(true);
  const unameRef = useRef();
  const emailRef = useRef();
  const passwordRef = useRef();
  const navigate = useNavigate();

  const authContext = useContext(AuthContext);

  const switchAuthModeHandler = () => {
    setIsLogin((prevState) => !prevState); // sets login to opposite of prev state
  };

    const newUser = () =>{
        const uname = unameRef.current.value;
        const password = passwordRef.current.value;
        const email = emailRef.current.value;

        fetch('http://localhost:8000/joinSite', {
            method: 'post',
            headers: {'Content-Type': "application/json; charset=utf-8"},
            body: JSON.stringify({
                'uname': uname,
                'password': password,
                'email' : email
            }),
        }).then((res) => {
            return res.json()
        }).then((data) => {
            // tell user thank you for joining, we will activate your account
            if (data.new_user=="true"){
                alert("Thanks for joining")
                navigate('/')
            }else{
                alert("Something went wrong, user name may be taken")
            }
        });

    }

    const newLogin = () =>{
        const uname = unameRef.current.value;
        const password = passwordRef.current.value;

        fetch('http://localhost:8000/login', {
            method: 'post',
            headers: {'Content-Type': "application/json; charset=utf-8"},
            body: JSON.stringify({
                'uname': uname,
                'password': password
            }),
        }).then((res) => {
            return res.json()
        }).then((data) => {
            if (data.sessionid != ""){
                authContext.login(data.sessionid, data.uname, data.role)
                navigate('/')
            }else{
                alert("Invalid login")
            }
        });
    }

    const submitHandler = (event) => {
        event.preventDefault();
        if (isLogin){
            newLogin()
        }else{
            newUser()
        }
    }

  return (
    <section >
      <h1>{isLogin ? 'Login' : 'Sign Up'}</h1>
      <form onSubmit={submitHandler}>
        <div >
          <label htmlFor='uname'>Your UserName</label>
          <input type='text' id='uname' ref={unameRef}  required />
        </div><br />
    {!isLogin ?<><div >
          <label htmlFor='email'>Your Email</label>
          <input type='text' id='email' ref={emailRef}  required />
        </div><br /></>
      : null}
        <div >
          <label htmlFor='password'>Your Password</label>
          <input type='password' id='password' ref={passwordRef} required />
        </div><br />
        <div >
          <button>{isLogin ? 'Login' : 'Create Account'}</button>
          <button
            type='button'
            onClick={switchAuthModeHandler}
          >
            {isLogin ? 'Create new account' : 'Login with existing account'}
          </button>
        </div>
      </form>
    </section>
  );
};

export default LoginForm;

