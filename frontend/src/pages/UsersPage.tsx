import { FormEvent, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable, TableColumn } from "@/components/ui/DataTable";
import { FormField } from "@/components/ui/FormField";
import { Modal } from "@/components/ui/Modal";
import { SelectInput } from "@/components/ui/SelectInput";
import { TableSkeleton } from "@/components/ui/TableSkeleton";
import { TextInput } from "@/components/ui/TextInput";
import {
  createUser,
  deleteUser,
  listUsers,
  type UserRecord,
  updateUser,
  updateUserPassword,
} from "@/services/users";

import styles from "./UsersPage.module.css";

type CreateUserForm = {
  username: string;
  password: string;
  role: string;
  is_active: string;
};

type CreateUserErrors = {
  username?: string;
  password?: string;
  global?: string;
};

export function UsersPage() {
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<CreateUserForm>({
    username: "",
    password: "",
    role: "operator",
    is_active: "true",
  });
  const [formErrors, setFormErrors] = useState<CreateUserErrors>({});
  const [formFeedback, setFormFeedback] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [tableMessage, setTableMessage] = useState<string | null>(null);
  const [tableError, setTableError] = useState<string | null>(null);
  const [passwordUser, setPasswordUser] = useState<UserRecord | null>(null);
  const [passwordValue, setPasswordValue] = useState("");
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [isUpdatingPassword, setIsUpdatingPassword] = useState(false);

  useEffect(() => {
    setIsLoading(true);
    setError(null);
    listUsers()
      .then((data) => {
        setUsers(data);
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : "Não foi possível carregar os usuários.";
        setError(message);
        setUsers([]);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const columns = useMemo<TableColumn<UserRecord>[]>(
    () => [
      { header: "Usuário", accessor: "username" },
      {
        header: "Papel",
        render: (user) => (
          <SelectInput
            value={user.role}
            onChange={async (event) => {
              setTableError(null);
              setTableMessage(null);
              try {
                const nextRole = event.target.value;
                await updateUser(user.id, { role: nextRole });
                setUsers((current) =>
                  current.map((item) => (item.id === user.id ? { ...item, role: nextRole } : item)),
                );
                setTableMessage(`Papel de ${user.username} atualizado.`);
              } catch (err) {
                const message = err instanceof Error ? err.message : "Não foi possível atualizar o usuário.";
                setTableError(message);
              }
            }}
          >
            <option value="operator">Operador</option>
            <option value="viewer">Visualizador</option>
            <option value="admin">Administrador</option>
          </SelectInput>
        ),
      },
      {
        header: "Status",
        render: (user) => (
          <SelectInput
            value={user.is_active ? "true" : "false"}
            onChange={async (event) => {
              setTableError(null);
              setTableMessage(null);
              try {
                const isActive = event.target.value === "true";
                await updateUser(user.id, { is_active: isActive });
                setUsers((current) =>
                  current.map((item) => (item.id === user.id ? { ...item, is_active: isActive } : item)),
                );
                setTableMessage(`Status de ${user.username} atualizado.`);
              } catch (err) {
                const message = err instanceof Error ? err.message : "Não foi possível atualizar o usuário.";
                setTableError(message);
              }
            }}
          >
            <option value="true">Ativo</option>
            <option value="false">Inativo</option>
          </SelectInput>
        ),
      },
      {
        header: "Ações",
        width: "220px",
        render: (user) => (
          <div className={styles.actions}>
            <Button size="sm" variant="secondary" type="button" onClick={() => openPasswordModal(user)}>
              Redefinir senha
            </Button>
            <Button size="sm" variant="danger" type="button" onClick={() => handleDelete(user)}>
              Excluir
            </Button>
          </div>
        ),
      },
    ],
    [],
  );

  const openPasswordModal = (user: UserRecord) => {
    setPasswordUser(user);
    setPasswordValue("");
    setPasswordError(null);
  };

  const closePasswordModal = () => {
    setPasswordUser(null);
    setPasswordValue("");
    setPasswordError(null);
    setIsUpdatingPassword(false);
  };

  const handleDelete = async (user: UserRecord) => {
    if (!window.confirm(`Deseja excluir o usuário ${user.username}?`)) {
      return;
    }
    setTableError(null);
    setTableMessage(null);
    try {
      await deleteUser(user.id);
      setUsers((current) => current.filter((item) => item.id !== user.id));
      setTableMessage(`Usuário ${user.username} removido.`);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível excluir o usuário.";
      setTableError(message);
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormErrors({});
    setFormFeedback(null);

    const errors: CreateUserErrors = {};
    if (form.username.trim().length < 3) {
      errors.username = "Informe um usuário com pelo menos 3 caracteres.";
    }
    if (form.password.length < 6) {
      errors.password = "A senha deve ter pelo menos 6 caracteres.";
    }

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    setIsSubmitting(true);
    try {
      await createUser({
        username: form.username.trim(),
        password: form.password,
        role: form.role,
        is_active: form.is_active === "true",
      });
      setFormFeedback("Usuário criado com sucesso.");
      setForm({ username: "", password: "", role: "operator", is_active: "true" });
      const refreshed = await listUsers();
      setUsers(refreshed);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível criar o usuário.";
      setFormErrors({ global: message });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePasswordSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!passwordUser) {
      return;
    }
    if (passwordValue.length < 6) {
      setPasswordError("A senha deve ter ao menos 6 caracteres.");
      return;
    }
    setPasswordError(null);
    setIsUpdatingPassword(true);
    try {
      await updateUserPassword(passwordUser.id, passwordValue);
      setTableMessage(`Senha de ${passwordUser.username} atualizada.`);
      closePasswordModal();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível redefinir a senha.";
      setPasswordError(message);
    } finally {
      setIsUpdatingPassword(false);
    }
  };

  return (
    <div className={styles.container}>
      <header className="page-header">
        <h1>Usuários</h1>
        <p>Controle o acesso da equipe ao portal com base nos cadastros existentes no backend.</p>
      </header>

      <div className={styles.grid}>
        <Card title="Novo usuário" subtitle="Somente administradores podem gerenciar estas credenciais.">
          <form className={styles.form} onSubmit={handleSubmit}>
            {formErrors.global ? <div className={styles.errorMessage}>{formErrors.global}</div> : null}
            {formFeedback ? (
              <div className={styles.successMessage} role="status" aria-live="polite">
                {formFeedback}
              </div>
            ) : null}

            <FormField label="Usuário" htmlFor="user-username" error={formErrors.username}>
              <TextInput
                id="user-username"
                value={form.username}
                onChange={(event) => setForm((current) => ({ ...current, username: event.target.value }))}
                hasError={Boolean(formErrors.username)}
                placeholder="jose.silva"
                required
              />
            </FormField>

            <FormField label="Senha" htmlFor="user-password" error={formErrors.password}>
              <TextInput
                id="user-password"
                type="password"
                value={form.password}
                onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))}
                hasError={Boolean(formErrors.password)}
                placeholder="mín. 6 caracteres"
                required
              />
            </FormField>

            <div className={styles.formRow}>
              <FormField label="Papel" htmlFor="user-role">
                <SelectInput
                  id="user-role"
                  value={form.role}
                  onChange={(event) => setForm((current) => ({ ...current, role: event.target.value }))}
                >
                  <option value="operator">Operador</option>
                  <option value="viewer">Visualizador</option>
                  <option value="admin">Administrador</option>
                </SelectInput>
              </FormField>

              <FormField label="Ativo" htmlFor="user-active">
                <SelectInput
                  id="user-active"
                  value={form.is_active}
                  onChange={(event) => setForm((current) => ({ ...current, is_active: event.target.value }))}
                >
                  <option value="true">Sim</option>
                  <option value="false">Não</option>
                </SelectInput>
              </FormField>
            </div>

            <div className={styles.formActions}>
              <Button type="submit" isLoading={isSubmitting} loadingText="Salvando...">
                Criar usuário
              </Button>
            </div>
          </form>
        </Card>

        <Card title="Contas cadastradas" subtitle="Sincronizado com os dados do Flask.">
          {error ? <div className={styles.errorMessage}>{error}</div> : null}
          {tableError ? <div className={styles.errorMessage}>{tableError}</div> : null}
          {tableMessage ? (
            <div className={styles.successMessage} role="status" aria-live="polite">
              {tableMessage}
            </div>
          ) : null}
          {isLoading ? <TableSkeleton columns={columns.length} /> : null}
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

      <Modal
        isOpen={Boolean(passwordUser)}
        onClose={closePasswordModal}
        title={passwordUser ? `Redefinir senha de ${passwordUser.username}` : "Redefinir senha"}
        footer={
          <>
            <Button variant="ghost" type="button" onClick={closePasswordModal}>
              Cancelar
            </Button>
            <Button
              type="submit"
              form="password-form"
              isLoading={isUpdatingPassword}
              loadingText="Salvando..."
            >
              Atualizar senha
            </Button>
          </>
        }
      >
        <form id="password-form" className={styles.form} onSubmit={handlePasswordSubmit}>
          {passwordError ? <div className={styles.errorMessage}>{passwordError}</div> : null}
          <FormField label="Nova senha" htmlFor="new-password" error={passwordError ?? undefined}>
            <TextInput
              id="new-password"
              type="password"
              value={passwordValue}
              onChange={(event) => setPasswordValue(event.target.value)}
              placeholder="mínimo de 6 caracteres"
              required
            />
          </FormField>
        </form>
      </Modal>
    </div>
  );
}
