import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Alert,
  CircularProgress,
  Paper,
} from '@mui/material';
import axios from 'axios';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';

const API_BASE_URL = 'http://localhost:8000';

function CustomerUpload() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && (selectedFile.name.endsWith('.xlsx') || selectedFile.name.endsWith('.csv'))) {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Please select a valid Excel (.xlsx) or CSV file');
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);

    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post(`${API_BASE_URL}/customers/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setSuccess(true);
      setTimeout(() => {
        navigate('/');
      }, 2000);
    } catch (err) {
      console.error('Error uploading file:', err);
      setError(err.response?.data?.detail || 'An error occurred during upload');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="dashboard-card">
      <CardContent>
        <Typography variant="h5" component="h2" gutterBottom className="dashboard-title">
          Upload Customer Data
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Upload an Excel or CSV file containing customer information. The file should include columns for:
          name, email, phone, address, city, state, country, and postal_code.
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2, bgcolor: 'rgba(211, 47, 47, 0.15)' }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2, bgcolor: 'rgba(46, 125, 50, 0.15)' }}>
            File uploaded successfully! Redirecting to dashboard...
          </Alert>
        )}

        <Paper 
          elevation={0} 
          sx={{ 
            p: 3, 
            mb: 3, 
            borderRadius: 2, 
            border: '1px dashed rgba(255, 255, 255, 0.3)',
            bgcolor: 'rgba(255, 255, 255, 0.05)',
            textAlign: 'center'
          }}
        >
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
            <CloudUploadIcon sx={{ fontSize: 48, color: '#2196f3', mb: 1 }} />
            
            <Button
              variant="contained"
              component="label"
              color="secondary"
              sx={{ 
                px: 3, 
                py: 1.2,
                borderRadius: 2,
                boxShadow: '0 4px 10px rgba(0,0,0,0.2)'
              }}
            >
              Select File
              <input
                type="file"
                hidden
                accept=".xlsx,.csv"
                onChange={handleFileChange}
              />
            </Button>

            {file && (
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 1,
                bgcolor: 'rgba(33, 150, 243, 0.1)',
                p: 1,
                borderRadius: 1,
                mt: 1
              }}>
                <InsertDriveFileIcon color="primary" />
                <Typography variant="body1">
                  {file.name}
                </Typography>
              </Box>
            )}
          </Box>
        </Paper>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
          <Button
            variant="outlined"
            color="inherit"
            onClick={() => navigate('/')}
          >
            Back to Dashboard
          </Button>
          
          <Button
            variant="contained"
            color="primary"
            onClick={handleUpload}
            disabled={!file || loading}
            sx={{ 
              px: 4,
              py: 1, 
              borderRadius: 2,
              background: !file || loading ? 'rgba(255,255,255,0.12)' : 'linear-gradient(45deg, #2196f3, #1e88e5)'
            }}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Upload'}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
}

export default CustomerUpload; 