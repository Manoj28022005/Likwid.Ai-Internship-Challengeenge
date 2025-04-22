import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import CustomerUpload from './components/CustomerUpload';
import Dashboard from './components/Dashboard';
import './styles.css';

// Create a dark theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2196f3', // Bright blue
    },
    secondary: {
      main: '#f50057', // Bright pink
    },
    background: {
      default: '#111827', // Dark blue-gray
      paper: '#1f2937', // Slightly lighter blue-gray
    },
    text: {
      primary: '#f3f4f6',
      secondary: '#d1d5db',
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 8px 16px 0 rgba(0,0,0,0.2)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
  },
  typography: {
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ flexGrow: 1, backgroundColor: '#111827', minHeight: '100vh' }}>
          <AppBar position="static" elevation={0} sx={{ backgroundColor: '#1f2937' }}>
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
                Likwid.Ai ERP - Customer Management
              </Typography>
            </Toolbar>
          </AppBar>
          <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/upload" element={<CustomerUpload />} />
            </Routes>
          </Container>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App; 