import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert } from 'react-bootstrap';
import axios from 'axios';

const Search = () => {
  const [states, setStates] = useState([]);
  const [cities, setCities] = useState([]);
  const [selectedState, setSelectedState] = useState('');
  const [selectedCity, setSelectedCity] = useState('');
  const [selectedBloodGroup, setSelectedBloodGroup] = useState('');
  const [searchType, setSearchType] = useState('blood_bank');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Fetch states
    const fetchStates = async () => {
      try {
        const response = await axios.get('/api/states');
        setStates(response.data);
      } catch (err) {
        setError('Failed to fetch states');
      }
    };
    fetchStates();
  }, []);

  useEffect(() => {
    // Fetch cities when state is selected
    const fetchCities = async () => {
      if (selectedState) {
        try {
          const response = await axios.get(`/api/cities/${selectedState}`);
          setCities(response.data);
          setSelectedCity('');
        } catch (err) {
          setError('Failed to fetch cities');
        }
      }
    };
    fetchCities();
  }, [selectedState]);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const endpoint = searchType === 'blood_bank' ? '/api/blood-banks' : '/api/donors';
      const response = await axios.get(endpoint, {
        params: {
          city_id: selectedCity,
          blood_group: selectedBloodGroup
        }
      });
      setResults(response.data);
    } catch (err) {
      setError('Failed to fetch results');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-section py-5 bg-light">
      <Container>
        <Row className="justify-content-center">
          <Col md={10}>
            <Card className="shadow">
              <Card.Header className="bg-danger text-white">
                <h3 className="text-center mb-0">Find Blood Banks and Donors</h3>
              </Card.Header>
              <Card.Body>
                <Form onSubmit={handleSearch}>
                  <Row>
                    <Col md={4} className="mb-3">
                      <Form.Label>State</Form.Label>
                      <Form.Select
                        value={selectedState}
                        onChange={(e) => setSelectedState(e.target.value)}
                        required
                      >
                        <option value="">Select State</option>
                        {states.map(state => (
                          <option key={state.id} value={state.id}>
                            {state.name}
                          </option>
                        ))}
                      </Form.Select>
                    </Col>

                    <Col md={4} className="mb-3">
                      <Form.Label>City</Form.Label>
                      <Form.Select
                        value={selectedCity}
                        onChange={(e) => setSelectedCity(e.target.value)}
                        required
                        disabled={!selectedState}
                      >
                        <option value="">Select City</option>
                        {cities.map(city => (
                          <option key={city.id} value={city.id}>
                            {city.name}
                          </option>
                        ))}
                      </Form.Select>
                    </Col>

                    <Col md={4} className="mb-3">
                      <Form.Label>Blood Group</Form.Label>
                      <Form.Select
                        value={selectedBloodGroup}
                        onChange={(e) => setSelectedBloodGroup(e.target.value)}
                      >
                        <option value="">All Blood Groups</option>
                        <option value="A+">A+</option>
                        <option value="A-">A-</option>
                        <option value="B+">B+</option>
                        <option value="B-">B-</option>
                        <option value="AB+">AB+</option>
                        <option value="AB-">AB-</option>
                        <option value="O+">O+</option>
                        <option value="O-">O-</option>
                      </Form.Select>
                    </Col>
                  </Row>

                  <Row>
                    <Col md={6} className="mb-3">
                      <Form.Label>Search For</Form.Label>
                      <Form.Select
                        value={searchType}
                        onChange={(e) => setSearchType(e.target.value)}
                        required
                      >
                        <option value="blood_bank">Blood Banks</option>
                        <option value="donor">Donors</option>
                      </Form.Select>
                    </Col>

                    <Col md={6} className="mb-3">
                      <Form.Label>&nbsp;</Form.Label>
                      <Button type="submit" variant="danger" className="w-100" disabled={loading}>
                        {loading ? 'Searching...' : 'Search'}
                      </Button>
                    </Col>
                  </Row>
                </Form>

                {error && <Alert variant="danger">{error}</Alert>}

                <div className="mt-4">
                  {results.length > 0 ? (
                    <Row>
                      {results.map(result => (
                        <Col md={6} key={result._id} className="mb-4">
                          <Card>
                            <Card.Header className="bg-danger text-white">
                              <h5 className="mb-0">{result.name}</h5>
                            </Card.Header>
                            <Card.Body>
                              {searchType === 'blood_bank' ? (
                                <>
                                  <p><strong>Address:</strong> {result.address}</p>
                                  <p><strong>City:</strong> {result.city}</p>
                                  <p><strong>Contact:</strong> {result.contactNumber}</p>
                                  <p><strong>Email:</strong> {result.email}</p>
                                  <p><strong>Available Blood Groups:</strong> {result.availableBloodGroups.join(', ')}</p>
                                </>
                              ) : (
                                <>
                                  <p><strong>Blood Group:</strong> {result.bloodGroup}</p>
                                  <p><strong>City:</strong> {result.city}</p>
                                  <p><strong>Contact:</strong> {result.phone}</p>
                                  <p><strong>Last Donation:</strong> {result.lastDonationDate || 'Never'}</p>
                                  <p><strong>Status:</strong> {result.isAvailable ? 'Available' : 'Unavailable'}</p>
                                </>
                              )}
                              <Button
                                variant="danger"
                                href={`/${searchType}/${result._id}`}
                              >
                                View Details
                              </Button>
                            </Card.Body>
                          </Card>
                        </Col>
                      ))}
                    </Row>
                  ) : (
                    !loading && <Alert variant="info">No results found</Alert>
                  )}
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default Search; 