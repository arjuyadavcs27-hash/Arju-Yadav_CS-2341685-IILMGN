import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Navbar as BootstrapNavbar, Nav, Container, Button } from 'react-bootstrap';

const Navbar = () => {
  const navigate = useNavigate();
  const isAuthenticated = localStorage.getItem('token');

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  return (
    <BootstrapNavbar bg="light" expand="lg" className="shadow-sm">
      <Container>
        <BootstrapNavbar.Brand as={Link} to="/" className="text-danger fw-bold">
          Blood Bank
        </BootstrapNavbar.Brand>
        <BootstrapNavbar.Toggle aria-controls="basic-navbar-nav" />
        <BootstrapNavbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link as={Link} to="/">Home</Nav.Link>
            <Nav.Link as={Link} to="/search">Search</Nav.Link>
            <Nav.Link as={Link} to="/donor/register">Become a Donor</Nav.Link>
            <Nav.Link as={Link} to="/blood-bank/register">Register Blood Bank</Nav.Link>
          </Nav>
          <Nav>
            {isAuthenticated ? (
              <Button variant="outline-danger" onClick={handleLogout}>
                Logout
              </Button>
            ) : (
              <Button variant="danger" as={Link} to="/login">
                Login
              </Button>
            )}
          </Nav>
        </BootstrapNavbar.Collapse>
      </Container>
    </BootstrapNavbar>
  );
};

export default Navbar; 