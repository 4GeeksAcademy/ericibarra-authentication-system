import React, { useEffect, useState } from 'react';
import { Container, Row, Col, Card, Alert } from 'react-bootstrap';

export const Private = () => {
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

    useEffect(() => {
        const fetchProtectedData = async () => {
            try {
                const token = sessionStorage.getItem('token');
                const response = await fetch(`${BACKEND_URL}api/protected`, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });

                if (!response.ok) throw new Error('Unauthorized access');

                const data = await response.json();
                setMessage(data.message || '¡Hola, solo puedes ver esto si estás logeado!');
            } catch (err) {
                console.error(err);
                setError('Acceso denegado. Por favor, inicia sesión.');
            }
        };

        fetchProtectedData();
    }, []);

    return (
        <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '100vh' }}>
            <Row>
                <Col>
                    <Card className="text-center shadow-lg p-4" style={{ borderRadius: '1rem' }}>
                        <Card.Body>
                            {error ? (
                                <Alert variant="danger">{error}</Alert>
                            ) : (
                                <Card.Text className="fs-4">{message}</Card.Text>
                            )}
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </Container>
    );
};
