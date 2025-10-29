import { FormEvent, useState } from "react";
import { Navigate, useLocation, type Location } from "react-router-dom";

import { useAuth } from "@/contexts/AuthContext";

import styles from "./LoginPage.module.css";

type LocationState = {
  from?: Location;
};

export function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const location = useLocation();
  const state = location.state as LocationState | null;
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (isAuthenticated) {
    const redirectTo = state?.from?.pathname ?? "/";
    return <Navigate to={redirectTo} replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    try {
      setIsSubmitting(true);
      await login(username, password);
    } catch (loginError) {
      setError((loginError as Error).message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.card}>
        <h1>Entrar</h1>
        <p className={styles.subtitle}>
          Primeiro acesso: <strong>admin / admin</strong>
        </p>
        {error ? <div className={styles.error}>{error}</div> : null}
        <form onSubmit={handleSubmit} className={styles.form}>
          <label className={styles.field}>
            <span>Usuário</span>
            <input
              name="username"
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
            />
          </label>
          <label className={styles.field}>
            <span>Senha</span>
            <input
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          <button type="submit" disabled={isSubmitting} className={styles.submit}>
            {isSubmitting ? "Entrando..." : "Entrar"}
          </button>
        </form>
        <p className={styles.footer}>Dúvidas? Procure o administrador da plataforma.</p>
      </div>
    </div>
  );
}
