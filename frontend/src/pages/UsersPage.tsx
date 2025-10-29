import { useEffect, useMemo, useState } from "react";

import { Card } from "@/components/ui/Card";
import { DataTable, TableColumn } from "@/components/ui/DataTable";
import { listUsers, type UserRecord } from "@/services/users";

import styles from "./UsersPage.module.css";

export function UsersPage() {
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setIsLoading(true);
    setError(null);

    listUsers()
      .then((data) => {
        if (active) {
          setUsers(data);
        }
      })
      .catch((err: unknown) => {
        if (active) {
          const message = err instanceof Error ? err.message : "Não foi possível carregar os usuários.";
          setError(message);
          setUsers([]);
        }
      })
      .finally(() => {
        if (active) {
          setIsLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  const columns = useMemo<TableColumn<UserRecord>[]>(
    () => [
      { header: "Usuário", accessor: "username" },
      { header: "Papel", accessor: "role" },
      {
        header: "Status",
        render: (user) => (user.is_active ? "Ativo" : "Inativo"),
      },
    ],
    [],
  );

  return (
    <div className={styles.container}>
      <header className="page-header">
        <h1>Usuários</h1>
        <p>Controle o acesso da equipe ao portal com base nos cadastros existentes no backend.</p>
      </header>

      <Card title="Contas cadastradas" subtitle="Sincronizado com os dados do Flask.">
        {error ? <div className={styles.errorMessage}>{error}</div> : null}
        {isLoading ? <div className={styles.loadingMessage}>Carregando usuários...</div> : null}
        {!isLoading && users.length === 0 && !error ? (
          <div className={styles.emptyState}>
            Nenhum usuário encontrado. Apenas administradores podem gerenciar esta área.
          </div>
        ) : null}
        {!isLoading && users.length > 0 ? (
          <DataTable columns={columns} data={users} keyExtractor={(user) => user.id.toString()} />
        ) : null}
      </Card>
    </div>
  );
}
