import axios from 'axios'
import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button, Divider, Form, Label, Segment } from 'semantic-ui-react'

function Login() {
  const [username, setUsername] = useState<string>('')
  const [password, setPassword] = useState<string>('')
  const [errorMsg, setErrorMsg] = useState<string>('')

  const logIn = async () => {
    try {
      await axios.post('/login', {
        username: username,
        password: password
      })
      // everything OK, go to the home
      window.location.href='/'
    }
    catch (error) {
      setErrorMsg(error.response.data.error)
    }
  }

  return (
    <Segment>
      <Link to="/register"><h3>New user? Register</h3></Link>
      <Segment>
        <Form>
          <Form.Group widths='equal'>
            <Form.Input label='Username' type='text' onChange={(e) => {setUsername(e.target.value)}} />
            <Form.Input label='Password' type='password' onChange={(e) => {setPassword(e.target.value)}} />
          </Form.Group>
          <Form.Button primary onClick={logIn}>Log in</Form.Button>
          {errorMsg ?
            <Label color='red' prompt>
              {errorMsg}
            </Label>
            :
            null}
      </Form>
      <Divider horizontal>Or</Divider>
      <Button
        color='red'
        content='Use your Google account'
        onClick={() => {window.location.href='/login/googlelogin'}}
      />
      </Segment>
    </Segment>
  )
}

export default Login
