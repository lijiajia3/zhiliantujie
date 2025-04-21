import React from 'react';
import Sidebar from '../components/Sidebar';
import { Outlet } from 'react-router-dom';

const MainLayout = () => {
  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {}
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          bottom: 0,
          width: 240,      
          overflowY: 'auto',
          backgroundColor: '#708090', 
        }}
      >
        <Sidebar />
      </div>

      {}
      <div
        style={{
          flex: 1,
          marginLeft: 240,           
          height: '100vh',
          overflowY: 'auto',
          padding: 20,
          backgroundColor: '#f7f9fc',
        }}
      >
        <Outlet />
      </div>
    </div>
  );
};

export default MainLayout;