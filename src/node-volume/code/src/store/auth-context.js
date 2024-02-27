import React, { useState, createContext } from 'react';

const AuthContext = React.createContext({
    sessionid: '',
    isLoggedIn: false,
    login: (sessionid) => {},
    logout: () => {},
    uname: '',
    role: '',
});

export const AuthContextProvider = (props) => {
    const initialSessionid = localStorage.getItem('sessionid'); // allows user to refresh app
    const initialUname = localStorage.getItem('uname'); // allows user to refresh app
    const initialRole = localStorage.getItem('role')

    const [sessionid, setSessionid] = useState(initialSessionid);
    const [uname, setUname] = useState(initialUname)
    const [role, setRole] = useState(initialRole)

    const userIsLoggedIn = !!sessionid; // returns true if string not empty

    const loginHandler = (sessionid, uname, role) => {
        setSessionid(sessionid);
        setUname(uname)
        setRole(role)
        localStorage.setItem('sessionid', sessionid)
        localStorage.setItem('uname', uname)
        localStorage.setItem('role', role)
    };

    const logoutHandler = () => {
        setSessionid(null)
        setUname(null)
        setRole(null)
        localStorage.removeItem('sessionid')
        localStorage.removeItem('uname')
        localStorage.removeItem('role')
    };

    const contextValue = {
        sessionid: sessionid,
        isLoggedIn: userIsLoggedIn,
        login: loginHandler,
        logout: logoutHandler,
        uname: uname,
        role: role
    };

    return <AuthContext.Provider value={contextValue}>
        {props.children}
        </AuthContext.Provider>
}

export default AuthContext;
