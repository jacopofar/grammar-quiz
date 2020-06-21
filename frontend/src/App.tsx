import axios from 'axios'
import React, { useEffect, useState } from 'react'
import { Button, Container, Dropdown, Grid, Menu } from 'semantic-ui-react'
import { Link, HashRouter as Router, Route, Switch } from 'react-router-dom'

import Login from './Login'
import Register from './Register'
import Study from './Study'


function App() {
  // user state: undefined when unknown, otherwise loggedIn set to true or false
  const [loggedInUser, setLoggedInUser] = useState<{loggedIn: boolean, name?: string}>()

  // check whether the user is logged in, and the name
  useEffect(() => {
    async function getMyIdentity() {
      const identity = (await axios.get('/login/whoami')).data
      if (!identity.authenticated){
        setLoggedInUser({loggedIn: false})
      }
      else {
        setLoggedInUser({loggedIn: true, name: identity.name})
      }
    }
    getMyIdentity()
  }, [])

  return (
    <Router basename={process.env.PUBLIC_URL}>
      <Menu fixed='top' inverted>
        <Container>
          <Menu.Item header>
            <a href="/">Grammar quiz</a>
          </Menu.Item>
          <Dropdown item simple text='Menu'>
            <Dropdown.Menu>
            {loggedInUser?.loggedIn ?
             <Button
             content={`logout ${loggedInUser.name}`}
             onClick={() => {
              axios.post('/login/logout').then(() =>{ window.location.href='/'})}
              }
            />
             :
             null}
              {/* <Dropdown.Item>List Item</Dropdown.Item>
              <Dropdown.Item>List Item</Dropdown.Item>
              <Dropdown.Divider />
              <Dropdown.Header>Header Item</Dropdown.Header>
              <Dropdown.Item>List Item</Dropdown.Item> */}
            </Dropdown.Menu>
          </Dropdown>
      </Container>
    </Menu>
    <Grid padded>
      <Grid.Column computer={2} only='computer'></Grid.Column>
      <Grid.Column computer={12} mobile={16} tablet={12}>

          <Switch>
            <Route path="/login">
                <Login />
            </Route>
            <Route path="/register">
              <Register />
            </Route>
            <Route exact path="/">
            {loggedInUser ?
              <Study
                loggedIn={loggedInUser.loggedIn}
              />
              :
              <p>Loading...</p>
            }
            </Route>
          </Switch>
      </Grid.Column>
      <Grid.Column computer={2} only='computer'></Grid.Column>
      </Grid>
    </Router>
  )
}

export default App
