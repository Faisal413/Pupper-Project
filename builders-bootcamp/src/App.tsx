import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { useState } from 'react'
import './App.css'
import { Authenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import { Amplify } from 'aws-amplify';
import { AppBar, Toolbar, Button } from '@mui/material';
import Home from './componets/home';
import ProductDetail from './componets/ProductDetile';

function App() {

  const user_pool_id = import.meta.env.VITE_USER_POOL_ID;
  const client_id = import.meta.env.VITE_CLIENT_ID;

  const formFields = {
    signUp: {
      email: {
        order: 1
      },
      given_name: {
        order: 2,
        label: 'First Name',
      },
      family_name: {
        order: 3,
        label: 'Last Name',
      },
      password: {
        order: 4
      },
      confirm_password: {
        order: 5
      }
    }
  };

  Amplify.configure({
    Auth: {
      Cognito: {
        userPoolId: user_pool_id,
        userPoolClientId: client_id,
        loginWith: {
          username: true,
          email: true,
        },
      }
    }
  });

  return (
    <Authenticator formFields={formFields}>
      {({ signOut, user }) => (
        <>
          <Router>
            <AppBar position="fixed">
              <Toolbar>
                <Button color="inherit" component={Link} to="/">Home</Button>
                <Button color="inherit" onClick={signOut}>Logout</Button>
              </Toolbar>
            </AppBar>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/products/:id" element={<ProductDetail/>}  />
            </Routes>
          </Router>
        </>
      )}
    </Authenticator>
  )
}

export default App