import React, { useState, useEffect } from 'react';
import axios from '../utils/request';
import { useNavigate } from 'react-router-dom';
import './LoginPage.css';
import { Link } from 'react-router-dom';

const LoginPage = () => {
  const [loginType, setLoginType] = useState('password'); 
  const [phone, setPhone] = useState('');
  const [emailOrPhone, setEmailOrPhone] = useState('');
  const [password, setPassword] = useState('');
  const [code, setCode] = useState('');
  const [countdown, setCountdown] = useState(0);
  const [recommendation, setRecommendation] = useState('');
  const [showRecommendation, setShowRecommendation] = useState(false);
  const navigate = useNavigate();
  
  useEffect(() => {
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');
    if (token && role) {
      console.log('🔁 已检测到登录状态，跳转中...');
      if (role === 'admin') {
        navigate('/admin');
      } else if (role === 'hr') {
        navigate('/hr');
      } else if (role === 'leader') {
        navigate('/leader/employees');
      } else if (role === 'employee') {
        navigate('/mytasks');
      }
    }
  }, []);

  const handlePasswordLogin = async () => {
    if (!emailOrPhone || !password) {
      alert("请输入用户名/邮箱/手机号和密码！");
      return;
    }
  
    console.log("🚀 提交登录请求:", { identifier: emailOrPhone, password });
  
    try {
      const response = await axios.post('/login', {
        identifier: emailOrPhone,
        password: password
      }, {
        headers: {
          "Content-Type": "application/json"
        }
      });
  
      console.log('✅ 密码登录成功', response.data);
  
      const user = response.data.user;
      const role = user?.role;
  
      if (!role) {
        console.warn('⚠️ 登录失败：未返回角色字段');
        alert('登录失败：用户信息缺失');
        return;
      }
  
      localStorage.setItem('token', response.data.token || 'placeholder');
      localStorage.setItem('role', role);
  
      console.log('➡️ 即将跳转到页面：', role);
  
      if (role === 'admin') {
        navigate('/admin');
        fetch('/recommendation')
          .then(res => res.json())
          .then(data => {
            setRecommendation(data?.message || '暂无推荐内容');
            setShowRecommendation(true);
          })
          .catch(err => console.error('获取推荐建议失败:', err));
      } else if (role === 'hr') {
        navigate('/hr');
      } else if (role === 'leader') {
        navigate('/leader/employees');
      } else if (role === 'employee') {
        navigate('/mytasks');
      } else {
        console.warn('⚠️ 身份未知，无法登录');
        alert('登录失败：未知身份');
      }
    } catch (error) {
      console.error('❌ 密码登录失败', error);
      console.error("❌ 登录异常：", error?.response?.data || error.message);
      alert('登录失败，请检查账号密码');
    }
  };

  const handleSendCode = async () => {
    if (!phone) {
      alert('请输入手机号');
      return;
    }
    try {
      await axios.post('/send-code', { phone });
      setCountdown(60);
      const timer = setInterval(() => {
        setCountdown(prev => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } catch (error) {
      console.error('❌ 验证码发送失败', error);
      alert('验证码发送失败，请稍后重试');
    }
  };

  const handlePhoneLogin = async () => {
    if (!phone || !code) {
      alert("请输入手机号和验证码！");
      return;
    }
    console.log("🚀 提交验证码登录请求:", { phone, code });
    try {
      if (!/^\d{11}$/.test(phone)) {
        alert("请输入有效的11位手机号！");
        return;
      }
      const response = await axios.post('/phone-login', {
        phone: phone,
        code: code
      });
      console.log('✅ 验证码登录成功', response.data);
      const role = response.data.role;
      localStorage.setItem('token', response.data.token || 'placeholder');
      localStorage.setItem('role', role);
      if (!role) {
        console.warn('⚠️ 登录失败：未返回角色字段');
        return;
      }
      if (role === 'admin') {
        navigate('/admin');
      } else if (role === 'hr') {
        navigate('/hr');
      } else if (role === 'leader') {
        navigate('/leader/employees');
      } else if (role === 'employee') {
        navigate('/mytasks');
      } else {
        console.warn('⚠️ 身份未知，无法登录');
      }
    } catch (error) {
      console.error('❌ 验证码登录失败', error);
      console.error("❌ 登录异常：", error?.response?.data || error.message);
      alert('验证码登录失败，请稍后重试');
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="form-section">
          <h1 className="title">智链图解 <span className="subtitle">动态平台</span></h1>
          <div className="tab-switch">
            <span
              className={`tab ${loginType === 'phone' ? 'active' : 'inactive'}`}
              onClick={() => setLoginType('phone')}
            >
              验证码登录
            </span>
            <span
              className={`tab ${loginType === 'password' ? 'active' : 'inactive'}`}
              onClick={() => setLoginType('password')}
            >
              密码登录
            </span>
          </div>
          <div className="input-wrapper">
            {loginType === 'password' ? (
              <>
                <div className="input-group">
                  <input
                    type="text"
                    placeholder="手机号/用户名/邮箱"
                    value={emailOrPhone}
                    onChange={(e) => setEmailOrPhone(e.target.value)}
                  />
                </div>
                <div className="input-group">
                  <input
                    type="password"
                    placeholder="请输入密码"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
              </>
            ) : (
              <>
                <div className="input-group">
                  <input
                    type="text"
                    placeholder="请输入手机号"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                  />
                </div>
                <div className="input-group">
                  <input
                    type="text"
                    placeholder="请输入验证码"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                  />
                </div>
                <div className="input-group">
                  <button className="send-code-btn" onClick={handleSendCode} disabled={countdown > 0}>
                    {countdown > 0 ? `重新发送 (${countdown}s)` : '发送验证码'}
                  </button>
                </div>
              </>
            )}
          </div>
          <div className="agreement">
            注册登录即代表已阅读并同意我们的 <Link to="/terms-of-service">用户协议</Link> 与 <Link to="/privacy-policy">隐私政策</Link>
          </div>
          <button className="login-btn" onClick={loginType === 'password' ? handlePasswordLogin : handlePhoneLogin}>
            登录
          </button>
          {showRecommendation && (
            <div style={{ marginTop: '20px', padding: '15px', border: '1px solid #ccc', borderRadius: '5px', backgroundColor: '#f9f9f9' }}>
              <h4>推荐录用建议</h4>
              <p>{recommendation}</p>
            </div>
          )}
          <div className="bottom-links">
            <Link to="/forgot-password">忘记密码</Link>
            <Link to="/register" style={{ float: 'right' }}>立即注册</Link>
          </div>
        </div>
        <div className="side-section" />
        </div>
      <div className="footer">Copyright©2025 瑞佳恒创</div>

      <div className="footer-links" style={{ textAlign: 'center', fontSize: '13px', color: '#888', marginTop: '10px' }}>
        <Link to="/about">关于</Link> · 
        <Link to="/contact" style={{ marginLeft: '8px' }}>联系我们</Link>
      </div>

      {!navigator.userAgent.toLowerCase().includes("electron") && (
  <div style={{ textAlign: 'center', fontSize: '13px', color: '#666', marginTop: '20px', marginBottom: '30px' }}>
    <h4 style={{ marginBottom: '8px', fontWeight: 'bold' }}>💻 智链图解客户端下载</h4>

    {(() => {
      const platform = navigator.platform.toLowerCase();
      const isMac = platform.includes("mac");
      const isWin = platform.includes("win");
      const isLinux = platform.includes("linux");

      const highlight = (active) => active ? { fontWeight: 'bold', color: '#007bff' } : {};

      return (
        <div style={{ lineHeight: '1.8' }}>
          <a
            href="http://113.46.143.235/downloads/zhiliantujie-1.0.0.dmg"
            target="_blank"
            rel="noopener noreferrer"
            style={highlight(isMac)}
          >🖥️ macOS (.dmg)</a>
          {" | "}
          <a
            href="http://113.46.143.235/downloads/zhiliantujie-1.0.0.exe"
            target="_blank"
            rel="noopener noreferrer"
            style={{ marginLeft: 6, ...highlight(isWin) }}
          >🪟 Windows (.exe)</a>
          {" | "}
          <a
            href="http://113.46.143.235/downloads/zhiliantujie-1.0.0.deb"
            target="_blank"
            rel="noopener noreferrer"
            style={{ marginLeft: 6, ...highlight(isLinux) }}
          >🐧 Linux (.deb)</a>
          {" | "}
          <a
            href="http://113.46.143.235/downloads/zhiliantujie-1.0.0.AppImage"
            target="_blank"
            rel="noopener noreferrer"
            style={{ marginLeft: 6, ...highlight(isLinux) }}
          >📦 Linux (.AppImage)</a>
       </div>
            );
          })()}
        </div>
      )}
    </div>
  );
};
export default LoginPage;