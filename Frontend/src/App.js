import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Outlet } from 'react-router-dom';
import CreateContest from './pages/staff/coding/CreateContest';
import ContestPage from './pages/staff/coding/ContestPage';
import StartContest from './pages/staff/coding/StartContest';
import SelectTestOption from './pages/staff/coding/SelectTestOption';
import FileUpload from './pages/staff/coding/FileUpload';
import ManualSelectUI from './pages/staff/coding/ManualSelectUI';
import HrUpload from './pages/staff/coding/HrUploadPage';
import OnebyOne from './pages/staff/coding/OnebyOne';
import ManualPage from './pages/staff/coding/ManualPage';
import ContestDashboard from './pages/staff/coding/ContestDashboard';
import Login from './pages/staff/Login';
import Signup from './pages/staff/Signup';
import Dashboard from './pages/staff/Dashboard';
import GeneralHome from './pages/GeneralHome';
import StudentRegister from './pages/student/StudentRegister';
import StudentLogin from './pages/student/StudentLogin';
import StudentDashboard from './pages/student/StudentDashboard';
import StudentProfile from './pages/student/StudentProfile';
import Navbar from './pages/student/Navbar';
import StaffNavbar from './pages/staff/StaffNavbar';
import TestInstructions from './pages/student/TestInstruction';
import ViewContest from './pages/staff/coding/ViewContest';
import Assesment from './pages/staff/coding/Assesment';
import QuestionsLibrary from './pages/staff/coding/QuestionsLibrary';
import Questions from './pages/staff/coding/Questions';
// Layout component for wrapping student routes
const StudentLayout = () => (
  <>
    <Navbar />
    <Outlet /> {/* Render nested routes */}
  </>
);

// Layout component for wrapping staff routes
const StaffLayout = () => (
  <>
    <StaffNavbar />
    <Outlet /> {/* Render nested routes */}
  </>
);

function App() {
  const [studentId, setStudentId] = useState(null);

  return (
    <Router>
      <Routes>
        {/* General Home */}
        <Route path="/" element={<GeneralHome />} />

        {/* Student Routes */}
        <Route path="/StudentRegister" element={<StudentRegister />} />
        <Route path="/StudentLogin" element={<StudentLogin onLogin={setStudentId} />} />
        <Route element={<StudentLayout />}>
          <Route path="/studentdashboard" element={<StudentDashboard />} />
          <Route path="/studentprofile" element={<StudentProfile studentId={studentId} />} />
        </Route>

        {/* Staff Routes */}
        <Route path="/stafflogin" element={<Login />} />
        <Route path="/staffsignup" element={<Signup />} />
        <Route element={<StaffLayout />}>
          <Route path="/staffdashboard" element={<Dashboard />} />
          <Route path="/assesment" element={<Assesment />} />
          <Route path="/coding" element={<ContestDashboard />} />
          <Route path="/SelectTestOption" element={<SelectTestOption />} />
          <Route path="/FileUpload" element={<FileUpload />} />
          <Route path="/ManualSelectUI" element={<ManualSelectUI />} />
          <Route path="/HrUpload/:contestId" element={<HrUpload />} />
          <Route path="/OnebyOne" element={<OnebyOne />} />
          <Route path="/ManualPage/:contestId" element={<ManualPage />} />
          <Route path="/CreateContest" element={<CreateContest />} />

          <Route path="/Questions/:contestId" element={<Questions />} />
          <Route path="/QuestionsLibrary/:contestId" element={<QuestionsLibrary />} />          
          <Route path="/StartContest" element={<StartContest />} />
          <Route path="/viewcontest/:contestId" element={<ViewContest />} />
        </Route>
        <Route path="/testinstructions/:testId" element={<TestInstructions />} />
        <Route path="/Contest/:testId" element={<ContestPage />} />

        {/* New View Contest Route */}
      </Routes>
    </Router>
  );
}

export default App;
