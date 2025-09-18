import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";

const API_URL = 'http://127.0.0.1:5000/api';

const ParceirosPage = () => {
    const [parceiros, setParceiros] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchParceiros = async () => {
            try {
                // Simulate a longer loading time to see the skeleton
                await new Promise(resolve => setTimeout(resolve, 1500));
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

    if (error) return (
      <div className="text-red-500 text-center p-4">
        Erro ao carregar parceiros: {error}
      </div>
    );

    return (
        <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">
                            Total de Parceiros
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        {loading ? (
                            <Skeleton className="h-8 w-1/4" />
                        ) : (
                            <div className="text-2xl font-bold">{parceiros.length}</div>
                        )}
                    </CardContent>
                </Card>
            </div>

            <div className="flex items-center justify-between">
                <h2 className="text-3xl font-bold tracking-tight">Gerenciamento de Parceiros</h2>
                <Button>Adicionar Parceiro</Button>
            </div>

            <Card>
                <CardContent>
                    {loading ? (
                        <div className="space-y-2 pt-6">
                            <Skeleton className="h-12 w-full" />
                            <Skeleton className="h-12 w-full" />
                            <Skeleton className="h-12 w-full" />
                            <Skeleton className="h-12 w-full" />
                            <Skeleton className="h-12 w-full" />
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>ID</TableHead>
                                    <TableHead>Nome</TableHead>
                                    <TableHead>CPF</TableHead>
                                    <TableHead>Email</TableHead>
                                    <TableHead>Cidade</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {parceiros.length > 0 ? (
                                    parceiros.map(parceiro => (
                                        <TableRow key={parceiro.id}>
                                            <TableCell className="font-medium">{parceiro.id}</TableCell>
                                            <TableCell>{parceiro.nome}</TableCell>
                                            <TableCell>{parceiro.cpf}</TableCell>
                                            <TableCell>{parceiro.email}</TableCell>
                                            <TableCell>{parceiro.cidade}</TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow>
                                        <TableCell colSpan="5" className="h-24 text-center">
                                            Nenhum parceiro encontrado.
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>
        </div>
    );
};

export default ParceirosPage;
