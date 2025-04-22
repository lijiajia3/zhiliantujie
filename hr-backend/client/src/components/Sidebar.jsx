import React from 'react';
import { useNavigate } from 'react-router-dom';

const Sidebar = () => {
  const role = localStorage.getItem('role');
  const navigate = useNavigate();

  const logout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const menu = [];

  if (role === 'admin') {
    menu.push({ name: '员工管理', path: '/employees' });
    menu.push({ name: '简历分析', path: '/resume-analysis' }); 
    menu.push({ name: '批量简历分析', path: '/batch-resume' }); 
    menu.push({ name: '推荐审批', path: '/admin/approve' });
    menu.push({ name: '动态追踪', path: '/admin/tracking' });
    menu.push({ name: '人才储备库', path: '/admin/pool' });
    menu.push({ name: '动态分析', path: '/leader/analysis' });
  }

  if (role === 'hr') {
    menu.push({ name: '员工管理', path: '/employees' });
    menu.push({ name: '推荐入职', path: '/hr/recommend' });
    menu.push({ name: '简历分析', path: '/resume-analysis' });
    menu.push({ name: '批量简历分析', path: '/batch-resume' }); 
    menu.push({ name: '人才储备库', path: '/admin/pool' });
    menu.push({ name: '动态分析', path: '/leader/analysis' });
  }

  if (role === 'leader') {
    menu.push({ name: '项目打分', path: '/tasks' });
    menu.push({ name: '员工管理', path: '/leader/employees' }); 
    menu.push({ name: '动态分析', path: '/leader/analysis' });
    menu.push({ name: '人才储备库', path: '/admin/pool' }); 
  }

  if (role === 'employee') {
    menu.push({ name: '我的任务', path: '/my-tasks' });
  }

  menu.push({ name: '我的信息', path: '/profile' });

  return (
    <div style={{
      width: 200,
      backgroundColor: '#708090',
      color: 'white',
      padding: 20
    }}>
      <h3>系统菜单</h3>
      {menu.map((item, index) => (
        <div
          key={index}
          style={{
            margin: '18px 0',
            cursor: 'pointer',
            transition: 'transform 0.2s ease, background-color 0.3s ease',
            padding: '6px 10px',
            borderRadius: '4px'
          }}
          onMouseEnter={e => {
            e.currentTarget.style.transform = 'translateX(5px)';
            e.currentTarget.style.backgroundColor = '#34495e';
          }}
          onMouseLeave={e => {
            e.currentTarget.style.transform = 'translateX(0)';
            e.currentTarget.style.backgroundColor = 'transparent';
          }}
          onClick={() => navigate(item.path)}
        >
          {item.name}
        </div>
      ))}
      <hr />
      <div style={{ cursor: 'pointer', marginTop: 10 }} onClick={logout}>
        🚪 退出登录
      </div>
    </div>
  );
};

export default Sidebar;