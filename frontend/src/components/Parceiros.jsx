import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Parceiros.css';

const API_URL = 'http://127.0.0.1:5000/api';

const ParceirosPage = () => {
    const [parceiros, setParceiros] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchParceiros = async () => {
            try {
                const response = await axios.get(`${API_URL}/parceiros/`);
                setParceiros(response.data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchParceiros();
    }, []);

    if (loading) return <p>Carregando parceiros...</p>;
    if (error) return <p>Erro ao carregar parceiros: {error}</p>;

    return (
        <div className="parceiros-container">
            <h2>Gerenciamento de Parceiros</h2>
            <table className="parceiros-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nome</th>
                        <th>CPF</th>
                        <th>Email</th>
                        <th>Cidade</th>
                    </tr>
                </thead>
                <tbody>
                    {parceiros.length > 0 ? (
                        parceiros.map(parceiro => (
                            <tr key={parceiro.id}>
                                <td>{parceiro.id}</td>
                                <td>{parceiro.nome}</td>
                                <td>{parceiro.cpf}</td>
                                <td>{parceiro.email}</td>
                                <td>{parceiro.cidade}</td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan="5">Nenhum parceiro encontrado.</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
};

export default ParceirosPage;
