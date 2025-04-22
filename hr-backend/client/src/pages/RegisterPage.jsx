import React, { useState, useEffect } from 'react';
import axios from 'axios';
 
import './LoginPage.css';

const RegisterPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('hr'); 
  const [phone, setPhone] = useState('');
  const [code, setCode] = useState('');
  const [codeSent, setCodeSent] = useState(false);
  const [countdown, setCountdown] = useState(0);

  useEffect(() => {
    let timer;
    if (countdown > 0) {
      timer = setTimeout(() => setCountdown(countdown - 1), 1000);
    } else {
      setCodeSent(false);
    }
    return () => clearTimeout(timer);
  }, [countdown]);

  const handleRegister = async (e) => {
    e.preventDefault();

    if (role === 'admin') {
      alert('管理员账户不可注册，请联系系统管理员');
      return;
    }

    try {
    console.log("🚀 正在验证验证码", { phone, code });
    const verifyRes = await axios.post('/validate-code-only', {
      phone: String(phone),
      code: String(code)
    });
    console.log("📦 验证响应：", verifyRes.data);
    if (!verifyRes.data || verifyRes.data.success !== true) {
        alert('验证码验证失败，请检查验证码是否正确');
        return;
      }

      const response = await axios.post('/register', {
        username,
        password,
        email,
        role,
        phone
      });
      alert(response.data.message); 
    } catch (error) {
      console.error('注册失败', error.response ? error.response.data : error);
      const errMsg = error.response?.data?.detail || '注册失败，请稍后再试';
      alert(errMsg);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="form-section">
          <h1 className="title">注册账号</h1>
          <div className="input-wrapper">
            <div className="input-group">
              <input
                type="text"
                placeholder="请输入用户名"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div className="input-group">
              <input
                type="email"
                placeholder="请输入邮箱"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="input-group">
              <input
                type="text"
                placeholder="请输入手机号"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
            </div>
            <div className="input-group">
              <button
                className="code-btn"
                disabled={codeSent}
                onClick={async (e) => {
                  if (!phone) {
                    alert('请输入手机号');
                    return;
                  }

                  try {
                    await axios.post('/send-code', { phone });
                    alert('验证码已发送');
                    setCodeSent(true);
                    setCountdown(60); 
                  } catch (error) {
                    alert('发送失败');
                  }
                }}
              >
                {codeSent ? `重新获取(${countdown})` : '获取验证码'}
              </button>
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
              <input
                type="password"
                placeholder="请输入密码"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <div className="input-group" style={{ marginTop: '20px' }}>
              <label style={{ marginBottom: '5px', fontSize: '14px', display: 'block' }}>请选择身份：</label>
              <select value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="employee">员工</option>
                <option value="hr">HR</option>
                <option value="leader">主管</option>
              </select>
            </div>
          </div>
          <button className="login-btn" onClick={(e) => handleRegister(e)}>
            注册
          </button>
          <div className="bottom-links">
            <a href="/login">返回登录</a>
          </div>
        </div>
        <div className="side-section" />
      </div>
      <div className="footer">Copyright©2025 瑞佳恒创</div>
    </div>
  );
};

export default RegisterPage;
