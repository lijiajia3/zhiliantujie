import React from 'react';

const Dashboard = () => {
  const username = localStorage.getItem('username');
  const role = localStorage.getItem('role');

  return (
    <div style={{ padding: 50 }}>
      <h1>欢迎你，{username} 👋</h1>
      <h2>你的角色是：{role}</h2>

      {role === 'admin' && (
        <div>
          <h3>🛠️ 管理员功能</h3>
          <p>可以管理用户权限、系统配置等</p>
        </div>
      )}

      {role === 'leader' && (
        <div>
          <h3>🧑‍💼 主管功能</h3>
          <p>可以审核员工、打分、查看报告</p>
        </div>
      )}

      {role === 'employee' && (
        <div>
          <h3>📝 员工功能</h3>
          <p>可以上传简历、提交项目报告</p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;