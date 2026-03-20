import React from 'react';
import { Link } from 'react-router-dom';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';

const Home = () => {
  return (
    <div>
      {/* Hero Section */}
      <div className="hero-section position-relative">
        <div className="hero-overlay"></div>
        <Container className="position-relative">
          <Row className="min-vh-100 align-items-center">
            <Col md={6}>
              <h1 className="display-4 text-white fw-bold mb-4">Save Lives, Donate Blood</h1>
              <p className="lead text-white mb-5">
                Join our community of blood donors and help save lives across India. 
                Your donation can make a difference.
              </p>
              <div className="d-flex gap-3">
                <Button as={Link} to="/donor/register" variant="danger" size="lg">
                  Become a Donor
                </Button>
                <Button as={Link} to="/blood-bank/register" variant="outline-light" size="lg">
                  Register Blood Bank
                </Button>
              </div>
            </Col>
          </Row>
        </Container>
      </div>

      {/* Features Section */}
      <div className="features-section py-5">
        <Container>
          <h2 className="text-center mb-5">Why Donate Blood?</h2>
          <Row>
            <Col md={4} className="mb-4">
              <Card className="h-100 border-0 shadow-sm">
                <Card.Body className="text-center">
                  <i className="fas fa-heartbeat fa-3x text-danger mb-3"></i>
                  <h4 className="card-title">Save Lives</h4>
                  <p className="card-text">
                    Your blood donation can save up to three lives. Every donation counts.
                  </p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4} className="mb-4">
              <Card className="h-100 border-0 shadow-sm">
                <Card.Body className="text-center">
                  <i className="fas fa-shield-alt fa-3x text-danger mb-3"></i>
                  <h4 className="card-title">Safe Process</h4>
                  <p className="card-text">
                    Our donation process is safe, hygienic, and supervised by medical professionals.
                  </p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4} className="mb-4">
              <Card className="h-100 border-0 shadow-sm">
                <Card.Body className="text-center">
                  <i className="fas fa-users fa-3x text-danger mb-3"></i>
                  <h4 className="card-title">Join Community</h4>
                  <p className="card-text">
                    Become part of a community dedicated to saving lives across India.
                  </p>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Container>
      </div>

      {/* Statistics Section */}
      <div className="statistics-section py-5 bg-light">
        <Container>
          <Row className="text-center">
            <Col md={3} className="mb-4">
              <h2 className="display-4 text-danger">1000+</h2>
              <p className="lead">Blood Banks</p>
            </Col>
            <Col md={3} className="mb-4">
              <h2 className="display-4 text-danger">50,000+</h2>
              <p className="lead">Active Donors</p>
            </Col>
            <Col md={3} className="mb-4">
              <h2 className="display-4 text-danger">1M+</h2>
              <p className="lead">Lives Saved</p>
            </Col>
            <Col md={3} className="mb-4">
              <h2 className="display-4 text-danger">28</h2>
              <p className="lead">States Covered</p>
            </Col>
          </Row>
        </Container>
      </div>
    </div>
  );
};

export default Home; 