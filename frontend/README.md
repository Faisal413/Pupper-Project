# Pupper Frontend

React + TypeScript application for the Pupper dog adoption platform using Vite, Material-UI, and AWS Amplify.

## Tech Stack

- **Vite** - Fast build tool
- **React 19** with TypeScript
- **Material-UI** - Component library
- **AWS Amplify** - Authentication (Cognito)
- **React Router** - Navigation

## Project Structure

```
src/
├── components/     # React components
├── types/         # TypeScript interfaces
├── App.tsx        # Main app with routing
└── main.tsx       # Entry point
```

## Features

- Display dogs available for adoption
- Material-UI card layout with responsive grid
- Clickable thumbnails that open original images
- AWS Cognito authentication (optional)
- TypeScript for type safety

## Getting Started

1. Install dependencies:
   ```
   npm install
   ```

2. Copy environment file:
   ```
   copy .env.example .env
   ```

3. Update `.env` with your configuration:
   ```
   VITE_API_URL=http://your-api-url
   VITE_USER_POOL_ID=your_cognito_pool_id
   VITE_CLIENT_ID=your_cognito_client_id
   ```

4. Start the development server:
   ```
   npm run dev
   ```

5. Open [http://localhost:5173](http://localhost:5173) to view it in the browser.

## API Integration

The app expects your REST API to have:
- `GET /dogs` - Returns array of dog objects matching the `Dog` interface

## Authentication

- If Cognito credentials are provided, authentication is required
- If no Cognito credentials, app runs without authentication
- Ready for Component 5 integration

## Build

To build the app for production:
```
npm run build
```