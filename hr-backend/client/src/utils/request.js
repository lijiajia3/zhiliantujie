// utils/request.js
import axios from "axios";

const request = axios.create({
  baseURL: "http://113.46.143.235",  
  timeout: 10000,
  withCredentials: true
});

request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default request;