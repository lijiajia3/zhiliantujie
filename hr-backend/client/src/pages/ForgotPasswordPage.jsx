import axios from 'axios';
import React, { useState } from 'react';

const ForgotPasswordPage = () => {
  const [step, setStep] = useState(1);
  const [identifier, setIdentifier] = useState('');
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');

  const handleSendCode = async (e) => {
    e.preventDefault();
    if (!/^\d{11}$/.test(identifier)) {
      alert("请输入有效的11位手机号码！");
      return;
    }
    try {
      await axios.post("/send-code", { phone: identifier });
      alert("验证码已发送，请注意查收！");
      setStep(2);
    } catch (error) {
      console.error("❌ 发送验证码失败", error);
      alert("发送验证码失败，请稍后重试！");
    }
  };

  const handleResetPassword = (e) => {
    e.preventDefault();
    console.log('验证验证码:', code, '设置新密码:', newPassword);
    alert('密码已成功重置，请使用新密码登录！');
  };

  return (
    <div style={{ padding: '50px', display: 'flex', justifyContent: 'center' }}>
      <div style={{ maxWidth: '400px', width: '100%' }}>
        <button
          onClick={() => window.location.href = '/login'}
          style={{
            marginBottom: '20px',
            padding: '6px 16px',
            backgroundColor: '#ccc',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          🔙 返回登录
        </button>
        <h2 style={{ marginBottom: '20px' }}>🔐 忘记密码</h2>
        {step === 1 && (
          <form onSubmit={handleSendCode}>
            <label htmlFor="identifier">请输入绑定的手机号：</label>
            <input
              type="text"
              id="identifier"
              name="identifier"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              placeholder="手机号"
              required
              style={{ width: '100%', padding: '10px', margin: '10px 0' }}
            />
            <button type="submit" style={{ padding: '10px 20px' }}>📨 发送验证码</button>
          </form>
        )}

        {step === 2 && (
          <form onSubmit={handleResetPassword}>
            <label htmlFor="code">请输入验证码：</label>
            <input
              type="text"
              id="code"
              name="code"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="验证码"
              required
              style={{ width: '100%', padding: '10px', margin: '10px 0' }}
            />
            <label htmlFor="newPassword">设置新密码：</label>
            <input
              type="password"
              id="newPassword"
              name="newPassword"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="新密码"
              required
              style={{ width: '100%', padding: '10px', margin: '10px 0' }}
            />
            <button type="submit" style={{ padding: '10px 20px' }}>✅ 提交新密码</button>
          </form>
        )}
      </div>
    </div>
  );
};

export default ForgotPasswordPage;