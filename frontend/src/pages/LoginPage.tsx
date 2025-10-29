import { FormEvent, useMemo, useState } from "react";
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
  const [touchedFields, setTouchedFields] = useState({ username: false, password: false });

  const usernameError = useMemo(() => {
    if (!username.trim()) {
      return "Informe o usuário.";
    }
    return null;
  }, [username]);

  const passwordError = useMemo(() => {
    if (!password) {
      return "Informe a senha.";
    }
    return null;
  }, [password]);

  const isFormValid = !usernameError && !passwordError;

  function markFieldAsTouched(field: "username" | "password") {
    setTouchedFields((prev) => ({ ...prev, [field]: true }));
  }

  if (isAuthenticated) {
    const redirectTo = state?.from?.pathname ?? "/";
    return <Navigate to={redirectTo} replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setTouchedFields({ username: true, password: true });

    if (!isFormValid) {
      setError("Preencha os campos obrigatórios.");
      return;
    }

    try {
      setIsSubmitting(true);
      await login(username.trim(), password);
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
          <label
            className={`${styles.field} ${
              touchedFields.username && usernameError ? styles.fieldInvalid : ""
            }`}
          >
            <span>Usuário</span>
            <input
              name="username"
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              onBlur={() => markFieldAsTouched("username")}
              required
            />
            {touchedFields.username && usernameError ? (
              <span className={styles.fieldError}>{usernameError}</span>
            ) : null}
          </label>
          <label
            className={`${styles.field} ${
              touchedFields.password && passwordError ? styles.fieldInvalid : ""
            }`}
          >
            <span>Senha</span>
            <input
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              onBlur={() => markFieldAsTouched("password")}
              required
            />
            {touchedFields.password && passwordError ? (
              <span className={styles.fieldError}>{passwordError}</span>
            ) : null}
          </label>
          <button
            type="submit"
            disabled={isSubmitting || !isFormValid}
            className={styles.submit}
          >
            {isSubmitting ? "Entrando..." : "Entrar"}
          </button>
        </form>
        <p className={styles.footer}>Dúvidas? Procure o administrador da plataforma.</p>
      </div>
    </div>
  );
}
