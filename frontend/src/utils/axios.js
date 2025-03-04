import axios from 'axios';

// Create an Axios instance with default configurations
const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000', // Your API base URL
  timeout: 10000, // Optional timeout for requests
  headers: {
    'Content-Type': 'application/json',
    // 'Authorization': 'Bearer YOUR_TOKEN' // Optional: add token if needed
  }
});

// Example of request interceptor (optional)
axiosInstance.interceptors.request.use(
  config => {
    // You can modify the request config here (e.g., add headers or log)
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Example of response interceptor (optional)
axiosInstance.interceptors.response.use(
  response => {
    // You can modify the response data here
    return response;
  },
  error => {
    // Handle response errors
    return Promise.reject(error);
  }
);


// Global Error Handling (Optional)
axiosInstance.interceptors.response.use(
    response => {
      return response;
    },
    error => {
      // Global error handling, e.g., showing a notification or logging out the user
      console.error('API Error:', error.response || error);
      return Promise.reject(error);
    }
  );
  

export default axiosInstance;
