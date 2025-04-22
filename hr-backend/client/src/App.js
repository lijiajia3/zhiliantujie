import React from 'react';
import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage.jsx';
import MainLayout from './layout/MainLayout';
import EmployeeManagePage from './pages/EmployeeManagePage';
import TaskScorePage from './pages/TaskScorePage';
import MyTaskPage from './pages/MyTaskPage';
import ProfilePage from './pages/ProfilePage';
import ResumeAnalysisPage from './pages/ResumeAnalysisPage';
import HRRecommend from './pages/HRRecommend';
import LeaderApprovePage from './pages/LeaderApprovePage';
import AdminTrackingPage from './pages/AdminTrackingPage';
import TalentPoolPage from './pages/TalentPoolPage';
import AdminEmployeePage from './pages/AdminEmployeePage';
import TermsOfServicePage from './pages/TermsOfServicePage';
import PrivacyPolicyPage from './pages/PrivacyPolicyPage';
import HRManageEmployeePage from './pages/HRManageEmployeePage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import RegisterPage from './pages/RegisterPage';
import HRBatchResumePage from './pages/HRBatchResumePage';
import LeaderEmployeePage from './pages/LeaderEmployeePage';
import LeaderTrackingPage from './pages/LeaderTrackingPage';
import AboutPage from './pages/AboutPage';
import ContactPage from './pages/ContactPage';

function App() {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!token) return;

    const publicPaths = ['/login', '/register', '/forgot-password', '/terms-of-service', '/privacy-policy'];
    const isPublicPath = publicPaths.includes(location.pathname);

    if (role && isPublicPath) {
      setTimeout(() => {
        if (role === 'admin') {
          navigate('/admin/employees', { replace: true });
        } else if (role === 'hr') {
          navigate('/hr/employees', { replace: true });
        } else if (role === 'leader') {
          navigate('/leader/employees', { replace: true });
        }
      }, 0);
    }
  }, []); 

  return (
      <Routes>
        <Route path="/about" element={<AboutPage />} />
        <Route path="/contact" element={<ContactPage />} />
        {!token ? (
          <>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/terms-of-service" element={<TermsOfServicePage />} />
            <Route path="/privacy-policy" element={<PrivacyPolicyPage />} />
            <Route path="*" element={<Navigate to="/login" />} />
          </>
        ) : (
          <>
            <Route path="/" element={<MainLayout />}>
              <Route index element={<ProfilePage />} />
              <Route path="profile" element={<ProfilePage />} />
              <Route path="employees" element={<EmployeeManagePage />} />
              <Route path="tasks" element={<TaskScorePage />} />
              <Route path="my-tasks" element={<MyTaskPage />} />
              <Route path="resume-analysis" element={<ResumeAnalysisPage />} />
              <Route path="hr/recommend" element={<HRRecommend />} />
              <Route path="hr/employees" element={<HRManageEmployeePage />} />
              <Route path="admin/employees" element={<AdminEmployeePage />} />
              <Route path="admin/approve" element={<LeaderApprovePage />} />
              <Route path="admin/tracking" element={<AdminTrackingPage />} />
              <Route path="admin/pool" element={<TalentPoolPage />} />
              <Route path="leader/employees" element={<LeaderEmployeePage />} />
              <Route path="leader/analysis" element={<LeaderTrackingPage />} />
              <Route path="batch-resume" element={<HRBatchResumePage />} />
              <Route path="*" element={<Navigate to="/" />} />
            </Route>
          </>
        )}
      </Routes>
  );
}

export default App;