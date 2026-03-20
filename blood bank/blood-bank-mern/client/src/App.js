import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import DonorRegister from './pages/DonorRegister';
import BloodBankRegister from './pages/BloodBankRegister';
import Search from './pages/Search';
import DonorProfile from './pages/DonorProfile';
import BloodBankProfile from './pages/BloodBankProfile';
import Login from './pages/Login';
import PrivateRoute from './components/PrivateRoute';

function App() {
  return (
    <Router>
      <Navbar />
      <Container fluid className="p-0">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search" element={<Search />} />
          <Route path="/donor/register" element={<DonorRegister />} />
          <Route path="/blood-bank/register" element={<BloodBankRegister />} />
          <Route path="/login" element={<Login />} />
          <Route path="/donor/:id" element={<DonorProfile />} />
          <Route path="/blood-bank/:id" element={<BloodBankProfile />} />
        </Routes>
      </Container>
    </Router>
  );
}

export default App; 