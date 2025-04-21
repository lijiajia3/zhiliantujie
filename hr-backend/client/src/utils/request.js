import axios from "axios";

// 创建 axios 实例
const request = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "/api",
  timeout: 10000,
  withCredentials: true, // 如果后端设置了 Access-Control-Allow-Credentials
});

// ✅ 请求拦截器，自动添加 token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default request;