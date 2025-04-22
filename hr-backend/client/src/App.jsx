import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import MainLayout from './layout/MainLayout';
import EmployeeManagePage from './pages/EmployeeManagePage';
import TaskScorePage from './pages/TaskScorePage';
import MyTaskPage from './pages/MyTaskPage';
import ProfilePage from './pages/ProfilePage';

function App() {
  const token = localStorage.getItem('token');

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        {token ? (
          <Route path="/" element={<MainLayout />}>
            <Route index element={<ProfilePage />} />
            <Route path="employees" element={<EmployeeManagePage />} />
            <Route path="tasks" element={<TaskScorePage />} />
            <Route path="my-tasks" element={<MyTaskPage />} />
            <Route path="profile" element={<ProfilePage />} />
          </Route>
        ) : (
          <Route path="*" element={<Navigate to="/login" />} />
        )}
      </Routes>
    </BrowserRouter>
  );
}

export default App;