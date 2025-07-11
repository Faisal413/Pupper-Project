export const config = {
  API_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  ENVIRONMENT: process.env.NODE_ENV || 'development',
  
  // Future Cognito configuration
  COGNITO_USER_POOL_ID: process.env.REACT_APP_COGNITO_USER_POOL_ID,
  COGNITO_CLIENT_ID: process.env.REACT_APP_COGNITO_CLIENT_ID,
};