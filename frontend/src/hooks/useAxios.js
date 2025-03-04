import { useState } from 'react';
import axiosInstance from '../utils/axios';
import { CONTENT_TYPES } from '../utils/contentTypes';  // Import content type constants

const useAxios = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Generalized function to make requests
  const request = async (method, url, body = null, contentType = CONTENT_TYPES.JSON, config = {}) => {
    setLoading(true);
    setError(null);

    // Set the headers dynamically based on the content type
    const headers = {
      'Content-Type': contentType,
      ...config.headers,  // Merge any additional headers passed in
    };

    // If the method is GET and there is a body, encode the body as query params
    if (method.toLowerCase() === 'get' && body) {
      const params = new URLSearchParams(body).toString();
      url = `${url}?${params}`;
    }

    try {
      const response = await axiosInstance({
        method,
        url,
        data: method !== 'get' ? body : null,  // For GET, body is not included in the data
        headers,  // Add headers to the request
        ...config, // Allow custom configurations to be passed
      });
      setData(response.data);
      return response;
    } catch (err) {
      setError(err.message || 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // GET request with URL parameter encoding
  const get = async (url, body = null, contentType = CONTENT_TYPES.JSON, config = {}) => {
    return await request('get', url, body, contentType, config);
  };

  // POST request
  const post = async (url, body, contentType = CONTENT_TYPES.JSON, config = {}) => {
    return await request('post', url, body, contentType, config);
  };

  // PUT request
  const put = async (url, body, contentType = CONTENT_TYPES.JSON, config = {}) => {
    return await request('put', url, body, contentType, config);
  };

  // DELETE request
  const del = async (url, config = {}) => {
    return await request('delete', url, null, CONTENT_TYPES.JSON, config);
  };

  return {
    data,
    loading,
    error,
    get,
    post,
    put,
    del,
  };
};

export default useAxios;
