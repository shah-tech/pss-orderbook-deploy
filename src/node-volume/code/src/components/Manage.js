import React, {useEffect, useContext, useState} from 'react';
import { Link, useNavigate  } from 'react-router-dom';
import Table from 'react-bootstrap/Table';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import axios from "axios";

import AuthContext from '../store/auth-context'

const Manage = (props) => {

	const authContext = useContext(AuthContext)
	const [users, setUsers] = useState([])
	const [userRows, setUserRows] = useState([])
	const [userChanges, setUserChanges] = useState({})

	useEffect(() => {
		axios.post(
			"http://localhost:8000/all_accounts",
			{
				uname: authContext.uname,
				sessionid: authContext.sessionid,
			}
		).then((response) => {
			setUsers(response.data)	
		})
	},[])

	useEffect(()=>{
		console.log(userChanges)
	},[userChanges])

	useEffect(() => {
		let rows = []
		users.map((user) => {
			rows.push(<tr>
				<td>{user.uname}</td>
				<td>
				{ user.uname != "admin" && (
				<Form.Select
				  defaultValue={user.uname+","+user.role}
				  id={user.uname}
				  onChange={
					e => {
					    let uname = e.target.value.split(',')[0]
					    let role = e.target.value.split(',')[1]
					    if (role == user.role){ // default role...
						role = "default"
					    }
					    setUserChanges(prevState => ({
						    ...prevState,
						    [uname]: role
					    }));
					}
				  }
				>
					<option value={user.uname+",admin"}>admin</option>
					<option value={user.uname+",it"}>it</option>
					<option value={user.uname+",user"} >user</option>
				</Form.Select> ) || ("admin")}

				</td>
				<td>{user.dateJoined}</td>
			</tr>)
		})
		setUserRows(rows)
	}, [users])

	return(
		<section>
		<Table striped bordered hover size="sm">
		 <thead>
			<tr>
			  <th>User Name</th>
			  <th>Role</th>
			  <th>Member Since</th>
			</tr>
		 </thead>
		 <tbody>
		{userRows}
		</tbody>
		</Table>
		<Button 
		  onClick ={
			() => {
				axios.post(
					"http://localhost:8000/update_roles",
					{
						uname: authContext.uname,
						sessionid: authContext.sessionid,
						roles:userChanges
					}
				).then((response) => {
				  alert("Changes applied")
				  window.location.reload()
				})
			}
		  }
		as="input" type="button" value="Save Changes" />
		{' '}
		<Button onClick = {
			() => {
				window.location.reload()
			}
		} variant="outline-primary">Cancel Changes</Button>
		</section>
	)
}

export default Manage;
