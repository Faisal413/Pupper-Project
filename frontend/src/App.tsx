import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import { Authenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import { Amplify } from 'aws-amplify';
import { AppBar, Toolbar, Button, Typography, Fab, ThemeProvider, CssBaseline, IconButton } from '@mui/material';
import { Add, DarkMode, LightMode } from '@mui/icons-material';
import { useState } from 'react';
import Home from './components/Home';
import AddDog from './components/AddDog';
import WaggedDogs from './components/WaggedDogs';
import { createAppTheme } from './theme';
import { useDarkMode } from './hooks/useDarkMode';

function App() {
  const user_pool_id = import.meta.env.VITE_USER_POOL_ID;
  const client_id = import.meta.env.VITE_CLIENT_ID;
  const [addDogOpen, setAddDogOpen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const { isDark, toggleDarkMode } = useDarkMode();
  const currentTheme = createAppTheme(isDark);

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

  // Only configure Amplify if Cognito credentials are provided
  if (user_pool_id && client_id) {
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
  }

  const handleDogAdded = () => {
    setRefreshKey(prev => prev + 1);
  };

  // If no Cognito config, show app without authentication
  if (!user_pool_id || !client_id) {
    return (
      <ThemeProvider theme={currentTheme}>
        <CssBaseline />
        <Router>
          <AppBar position="fixed" elevation={0} sx={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
            backdropFilter: 'blur(20px)',
            borderBottom: 'none',
            color: 'white',
            top: 0,
            zIndex: 1200,
            height: { xs: '70px', sm: '80px', md: '90px' },
            boxShadow: '0 8px 32px rgba(102,126,234,0.3)'
          }}>
            <Toolbar sx={{ 
              py: { xs: 1, sm: 1.5, md: 2 },
              minHeight: { xs: '70px', sm: '80px', md: '90px' },
              px: 0,
              maxWidth: { xs: '100%', sm: '90%', md: '80%', lg: '70%' },
              mx: 'auto',
              width: '100%'
            }}>
              <Typography variant="h6" component="div" sx={{ 
                flexGrow: 1, 
                fontWeight: 900,
                fontSize: { xs: '1.4rem', sm: '1.6rem', md: '1.8rem' },
                color: 'white',
                textShadow: '0 2px 10px rgba(0,0,0,0.3)',
                letterSpacing: '-0.02em',
                background: 'linear-gradient(45deg, #ffffff 30%, #f0f8ff 90%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                textAlign: 'left',
                pl: { xs: 2, sm: 3, md: 4 }
              }}>
                🐕 Pupper
              </Typography>
              <Button 
                color="inherit" 
                component={Link} 
                to="/"
                sx={{ 
                  mx: 0.5, 
                  color: 'rgba(255,255,255,0.9)', 
                  borderRadius: 3,
                  px: 3,
                  py: 1.5,
                  fontWeight: 600,
                  fontSize: { xs: '0.9rem', sm: '1rem' },
                  background: 'rgba(255,255,255,0.1)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  '&:hover': { 
                    background: 'rgba(255,255,255,0.2)',
                    transform: 'translateY(-2px) scale(1.05)',
                    boxShadow: '0 8px 25px rgba(255,255,255,0.2)'
                  },
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                }}
              >
                Home
              </Button>
              <Button 
                color="inherit" 
                component={Link} 
                to="/wagged"
                sx={{ 
                  mx: 0.5, 
                  color: 'rgba(255,255,255,0.9)', 
                  borderRadius: 3,
                  px: 3,
                  py: 1.5,
                  fontWeight: 600,
                  fontSize: { xs: '0.9rem', sm: '1rem' },
                  background: 'rgba(255,255,255,0.1)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  '&:hover': { 
                    background: 'rgba(255,255,255,0.2)',
                    transform: 'translateY(-2px) scale(1.05)',
                    boxShadow: '0 8px 25px rgba(255,255,255,0.2)'
                  },
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                }}
              >
                My Wagged Dogs
              </Button>
              <IconButton
                onClick={toggleDarkMode}
                sx={{
                  ml: 1,
                  color: 'rgba(255,255,255,0.9)',
                  background: 'rgba(255,255,255,0.1)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: 3,
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    background: 'rgba(255,255,255,0.2)',
                    transform: 'rotate(360deg) scale(1.1)',
                    boxShadow: '0 8px 25px rgba(255,255,255,0.2)'
                  }
                }}
              >
                {isDark ? <LightMode /> : <DarkMode />}
              </IconButton>
            </Toolbar>
          </AppBar>
          <Routes>
            <Route path="/" element={<Home key={refreshKey} />} />
            <Route path="/wagged" element={<WaggedDogs />} />
          </Routes>
          <Fab
            color="primary"
            aria-label="add dog"
            sx={{ 
              position: 'fixed', 
              bottom: 24, 
              right: 24,
              boxShadow: '0 8px 25px rgba(45,55,72,0.2)',
              '&:hover': {
                boxShadow: '0 12px 35px rgba(45,55,72,0.3)',
              }
            }}
            onClick={() => setAddDogOpen(true)}
          >
            <Add />
          </Fab>
          <AddDog
            open={addDogOpen}
            onClose={() => setAddDogOpen(false)}
            onDogAdded={handleDogAdded}
          />
        </Router>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={currentTheme}>
      <CssBaseline />
      <Authenticator formFields={formFields}>
        {({ signOut, user }) => (
          <>
            <Router>
              <AppBar position="fixed" elevation={0} sx={{ 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
                backdropFilter: 'blur(20px)',
                borderBottom: 'none',
                color: 'white',
                top: 0,
                zIndex: 1200,
                height: { xs: '70px', sm: '80px', md: '90px' },
                boxShadow: '0 8px 32px rgba(102,126,234,0.3)'
              }}>
                <Toolbar sx={{ 
                  py: { xs: 1, sm: 1.5, md: 2 },
                  minHeight: { xs: '70px', sm: '80px', md: '90px' },
                  px: 0,
                  maxWidth: { xs: '100%', sm: '90%', md: '80%', lg: '70%' },
                  mx: 'auto',
                  width: '100%'
                }}>
                  <Typography variant="h6" component="div" sx={{ 
                    flexGrow: 1, 
                    fontWeight: 900,
                    fontSize: { xs: '1.4rem', sm: '1.6rem', md: '1.8rem' },
                    color: 'white',
                    textShadow: '0 2px 10px rgba(0,0,0,0.3)',
                    letterSpacing: '-0.02em',
                    background: 'linear-gradient(45deg, #ffffff 30%, #f0f8ff 90%)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    textAlign: 'left',
                    pl: { xs: 2, sm: 3, md: 4 }
                  }}>
                    🐕 Pupper
                  </Typography>
                  <Button 
                    color="inherit" 
                    component={Link} 
                    to="/"
                    sx={{ 
                      mx: 0.5, 
                      color: 'rgba(255,255,255,0.9)', 
                      borderRadius: 3,
                      px: 3,
                      py: 1.5,
                      fontWeight: 600,
                      fontSize: { xs: '0.9rem', sm: '1rem' },
                      background: 'rgba(255,255,255,0.1)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      '&:hover': { 
                        background: 'rgba(255,255,255,0.2)',
                        transform: 'translateY(-2px) scale(1.05)',
                        boxShadow: '0 8px 25px rgba(255,255,255,0.2)'
                      },
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                    }}
                  >
                    Home
                  </Button>
                  <Button 
                    color="inherit" 
                    component={Link} 
                    to="/wagged"
                    sx={{ 
                      mx: 0.5, 
                      color: 'rgba(255,255,255,0.9)', 
                      borderRadius: 3,
                      px: 3,
                      py: 1.5,
                      fontWeight: 600,
                      fontSize: { xs: '0.9rem', sm: '1rem' },
                      background: 'rgba(255,255,255,0.1)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      '&:hover': { 
                        background: 'rgba(255,255,255,0.2)',
                        transform: 'translateY(-2px) scale(1.05)',
                        boxShadow: '0 8px 25px rgba(255,255,255,0.2)'
                      },
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                    }}
                  >
                    My Wagged Dogs
                  </Button>
                  <IconButton
                    onClick={toggleDarkMode}
                    sx={{
                      ml: 1,
                      color: 'rgba(255,255,255,0.9)',
                      background: 'rgba(255,255,255,0.1)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: 3,
                      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                      '&:hover': {
                        background: 'rgba(255,255,255,0.2)',
                        transform: 'rotate(360deg) scale(1.1)',
                        boxShadow: '0 8px 25px rgba(255,255,255,0.2)'
                      }
                    }}
                  >
                    {isDark ? <LightMode /> : <DarkMode />}
                  </IconButton>
                  <Typography variant="body2" sx={{ 
                    mr: 2, 
                    color: 'rgba(255,255,255,0.8)',
                    fontWeight: 500,
                    fontSize: { xs: '0.85rem', sm: '0.9rem' }
                  }}>
                    Welcome, {user?.signInDetails?.loginId}
                  </Typography>
                  <Button 
                    color="inherit" 
                    onClick={signOut}
                    sx={{ 
                      color: 'rgba(255,255,255,0.9)', 
                      borderRadius: 3,
                      px: 3,
                      py: 1.5,
                      fontWeight: 600,
                      fontSize: { xs: '0.9rem', sm: '1rem' },
                      background: 'rgba(255,255,255,0.1)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      '&:hover': { 
                        background: 'rgba(255,255,255,0.2)',
                        transform: 'translateY(-2px) scale(1.05)',
                        boxShadow: '0 8px 25px rgba(255,255,255,0.2)'
                      },
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                    }}
                  >
                    Logout
                  </Button>
                </Toolbar>
              </AppBar>
              <Routes>
                <Route path="/" element={<Home key={refreshKey} />} />
                <Route path="/wagged" element={<WaggedDogs />} />
              </Routes>
              <Fab
                color="primary"
                aria-label="add dog"
                sx={{ 
                  position: 'fixed', 
                  bottom: 24, 
                  right: 24,
                  boxShadow: '0 8px 25px rgba(45,55,72,0.2)',
                  '&:hover': {
                    boxShadow: '0 12px 35px rgba(45,55,72,0.3)',
                  }
                }}
                onClick={() => setAddDogOpen(true)}
              >
                <Add />
              </Fab>
              <AddDog
                open={addDogOpen}
                onClose={() => setAddDogOpen(false)}
                onDogAdded={handleDogAdded}
              />
            </Router>
          </>
        )}
      </Authenticator>
    </ThemeProvider>
  );
}


export default App;