import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
} from '@mui/material';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Chart colors
const GEOGRAPHY_COLORS = ['#4ade80', '#34d399', '#10b981', '#059669', '#047857', '#065f46', '#064e3b', '#022c22'];
const SALES_COLORS = ['#f59e0b', '#fbbf24', '#f59e0b', '#d97706', '#b45309', '#92400e', '#78350f', '#663c00'];
const PRODUCT_COLORS = ['#ec4899', '#f472b6', '#db2777', '#be185d', '#9d174d', '#831843', '#701a75', '#4a044e'];

function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [geographyData, setGeographyData] = useState([]);
  const [salesData, setSalesData] = useState([]);
  const [productData, setProductData] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const navigate = useNavigate();

  const handleResetData = async () => {
    setOpenDialog(false);
    setLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/customers/reset`);
      // Refetch data after reset
      fetchData();
    } catch (err) {
      console.error('Error resetting data:', err);
      setError('Failed to reset data');
      setLoading(false);
    }
  };

  const fetchData = async () => {
    try {
      const [geoResponse, salesResponse, productResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/customers/top-by-geography`),
        axios.get(`${API_BASE_URL}/customers/top-by-sales`),
        axios.get(`${API_BASE_URL}/customers/top-by-products`),
      ]);

      setGeographyData(geoResponse.data);
      setSalesData(salesResponse.data);
      setProductData(productResponse.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to fetch dashboard data');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <Box className="loading-container">
        <CircularProgress size={60} thickness={4} color="secondary" />
      </Box>
    );
  }

  if (error) {
    return (
      <Card className="dashboard-card">
        <CardContent>
          <Typography color="error">{error}</Typography>
        </CardContent>
      </Card>
    );
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="label" style={{ fontWeight: 'bold', marginBottom: '8px' }}>{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color, margin: '4px 0' }}>
              {`${entry.name}: ${entry.value.toLocaleString()}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const ProductTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="custom-tooltip">
          <p style={{ fontWeight: 'bold', marginBottom: '8px' }}>{data.customer_name}</p>
          <p><strong>Product:</strong> {data.product_name}</p>
          <p><strong>Quantity:</strong> {data.total_quantity.toLocaleString()}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" className="dashboard-title">Customer Analytics Dashboard</Typography>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            color="error"
            onClick={() => setOpenDialog(true)}
          >
            Reset Data
          </Button>
          <Button
            variant="contained"
            color="secondary"
            onClick={() => navigate('/upload')}
            sx={{ px: 3, py: 1 }}
          >
            Upload New Customers
          </Button>
        </Box>
      </Box>

      {/* Confirmation Dialog */}
      <Dialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
      >
        <DialogTitle>Reset Data?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            This will delete all customer and sales data. This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)} color="inherit">Cancel</Button>
          <Button onClick={handleResetData} color="error">Reset</Button>
        </DialogActions>
      </Dialog>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card className="dashboard-card">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Customers by Geography
              </Typography>
              <Box height={400}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={geographyData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="country" 
                      angle={-45}
                      textAnchor="end"
                      height={70}
                      interval={0}
                    />
                    <YAxis />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Bar 
                      dataKey="customer_count" 
                      name="Number of Customers" 
                      className="geography-bar"
                    >
                      {geographyData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={GEOGRAPHY_COLORS[index % GEOGRAPHY_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card className="dashboard-card">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Customers by Sales Volume
              </Typography>
              <Box height={300}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={salesData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="customer_name" 
                      angle={-45}
                      textAnchor="end"
                      height={70}
                      interval={0}
                    />
                    <YAxis tickFormatter={(value) => value.toLocaleString()} />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Bar 
                      dataKey="total_sales" 
                      name="Total Sales" 
                      className="sales-bar"
                    >
                      {salesData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={SALES_COLORS[index % SALES_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card className="dashboard-card">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Customer-Product Combinations
              </Typography>
              <Box height={300}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={productData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="customer_name"
                      angle={-45}
                      textAnchor="end"
                      height={70}
                      interval={0}
                    />
                    <YAxis />
                    <Tooltip content={<ProductTooltip />} />
                    <Legend />
                    <Bar 
                      dataKey="total_quantity" 
                      name="Quantity Purchased" 
                      className="product-bar"
                    >
                      {productData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={PRODUCT_COLORS[index % PRODUCT_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Add pie chart for geography data */}
        <Grid item xs={12}>
          <Card className="dashboard-card">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Customer Distribution by Geography
              </Typography>
              <Box height={400} display="flex" justifyContent="center">
                <ResponsiveContainer width="80%" height="100%">
                  <PieChart>
                    <Pie
                      data={geographyData}
                      cx="50%"
                      cy="50%"
                      labelLine={true}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={150}
                      fill="#8884d8"
                      dataKey="customer_count"
                      nameKey="country"
                    >
                      {geographyData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={GEOGRAPHY_COLORS[index % GEOGRAPHY_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value, name, props) => [value.toLocaleString(), name]}
                      content={<CustomTooltip />} 
                    />
                    <Legend layout="horizontal" verticalAlign="bottom" align="center" />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard; 