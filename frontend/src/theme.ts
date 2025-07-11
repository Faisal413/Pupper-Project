import { createTheme } from '@mui/material/styles';

export const createAppTheme = (isDark: boolean) => createTheme({
  palette: {
    mode: isDark ? 'dark' : 'light',
    primary: {
      main: isDark ? '#4A90E2' : '#2D3748',
      light: isDark ? '#6BA3F0' : '#4A5568',
      dark: isDark ? '#357ABD' : '#1A202C',
    },
    secondary: {
      main: isDark ? '#A0AEC0' : '#718096',
      light: isDark ? '#CBD5E0' : '#A0AEC0',
      dark: isDark ? '#718096' : '#4A5568',
    },
    background: {
      default: isDark ? '#0F1419' : '#FAFAFA',
      paper: isDark ? '#1A202C' : '#FFFFFF',
    },
    text: {
      primary: isDark ? '#F7FAFC' : '#2D3748',
      secondary: isDark ? '#A0AEC0' : '#718096',
    },
    grey: {
      50: isDark ? '#2D3748' : '#F7FAFC',
      100: isDark ? '#4A5568' : '#EDF2F7',
      200: isDark ? '#718096' : '#E2E8F0',
      300: isDark ? '#A0AEC0' : '#CBD5E0',
      400: isDark ? '#CBD5E0' : '#A0AEC0',
      500: isDark ? '#E2E8F0' : '#718096',
    },
  },
  transitions: {
    duration: {
      standard: 300,
      complex: 375,
    },
  },
  typography: {
    fontFamily: '"Inter", "Segoe UI", "Roboto", sans-serif',
    h1: {
      fontWeight: 700,
      letterSpacing: '-0.025em',
    },
    h3: {
      fontWeight: 600,
      letterSpacing: '-0.025em',
    },
    h5: {
      fontWeight: 600,
      letterSpacing: '-0.01em',
    },
    h6: {
      fontWeight: 500,
      letterSpacing: '-0.01em',
    },
    body1: {
      lineHeight: 1.6,
    },
    body2: {
      lineHeight: 1.5,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: 8,
          padding: '10px 24px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #E2E8F0',
          borderRadius: 16,
          '&:hover': {
            boxShadow: '0 8px 25px rgba(0,0,0,0.1)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            backgroundColor: '#FFFFFF',
            '& fieldset': {
              borderColor: '#E2E8F0',
            },
            '&:hover fieldset': {
              borderColor: '#CBD5E0',
            },
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #E2E8F0',
          borderRadius: 12,
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          fontWeight: 500,
        },
      },
    },
  },
});

// Legacy theme for backward compatibility
export const theme = createAppTheme(false);