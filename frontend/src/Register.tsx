import axios from 'axios'
import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button, Divider, Form, Label, Segment } from 'semantic-ui-react'

import PrivacyNotice from './PrivacyNotice'

function Register() {
  const [acceptedPrivacy, setAcceptedPrivacy] = useState<boolean>(false)
  const [username, setUsername] = useState<string>('')
  const [password, setPassword] = useState<string>('')
  const [password2, setPassword2] = useState<string>('')
  const [errorMsg, setErrorMsg] = useState<string>('')


  const createAccount = async () => {
    try {
      await axios.post('/register_user', {
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
      <Link to="/login"><h3>Already an user? Log in</h3></Link>
      <PrivacyNotice />
      <Segment>
        <Form>
          <Form.Group widths='equal'>
            <Form.Input label='Username' type='text' onChange={(e) => {setUsername(e.target.value)}} />
            <Form.Input label='Password' type='password'
              onChange={(e) => {
                setPassword(e.target.value)
                if (e.target.value && (password2 !== e.target.value)) {
                  setErrorMsg('The passwords do not match')
                }
                else {
                  setErrorMsg('')
                }
            }
              } />
            <Form.Input label='Confirm password' type='password'
              onChange={(e) => {
                setPassword2(e.target.value)
                if (e.target.value && (password !== e.target.value)) {
                  setErrorMsg('The passwords do not match')
                }
                else {
                  setErrorMsg('')
                }
              }
              } />
            {errorMsg ?
            <Label color='red' prompt>
              {errorMsg}
            </Label>
            :
            null}
          </Form.Group>
          <Form.Checkbox
            label='I understand and accept the privacy notice'
            checked={acceptedPrivacy}
            onChange={()=>{setAcceptedPrivacy(!acceptedPrivacy)}}
            />
            <p color='red'>Ciaone</p>
          <Form.Button primary disabled={!acceptedPrivacy} onClick={createAccount}>Create account</Form.Button>
      </Form>
      <Divider horizontal>Or</Divider>
      <Form>
        <Form.Checkbox
              label='I understand and accept the privacy notice'
              checked={acceptedPrivacy}
              onChange={()=>{setAcceptedPrivacy(!acceptedPrivacy)}}
              />
        <Button
          color='red'
          content='Use your Google account'
          disabled={!acceptedPrivacy}
          onClick={() => {window.location.href='/login/googlelogin'}}
        />
      </Form>
      </Segment>
    </Segment>
  )
}

export default Register
