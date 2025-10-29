import { NavLink } from "react-router-dom";

import { useAuth } from "@/contexts/AuthContext";

import styles from "./TopNav.module.css";

const NAV_LINKS = [
  { to: "/", label: "Início", requiresAuth: true },
  { to: "/parceiros", label: "Parceiros", requiresAuth: true },
  { to: "/lojas", label: "Lojas", requiresAuth: true },
  { to: "/conectar", label: "Conectar", requiresAuth: false },
  { to: "/comprovantes", label: "Comprovantes", requiresAuth: true },
  { to: "/relatorios", label: "Relatórios", requiresAuth: true },
];

const USER_LINKS = [
  { to: "/usuarios", label: "Usuários" },
  { to: "/account", label: "Minha Conta" },
];

export function TopNav() {
  const { isAuthenticated, logout } = useAuth();

  return (
    <nav className={styles.nav}>
      <div className={styles.group}>
        <span className={styles.brand}>Disagua</span>
        {NAV_LINKS.filter((link) => (link.requiresAuth ? isAuthenticated : true)).map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              [styles.link, isActive ? styles.linkActive : undefined].filter(Boolean).join(" ")
            }
            end={to === "/"}
          >
            {label}
          </NavLink>
        ))}
      </div>
      <div className={styles.group}>
        {isAuthenticated ? (
          <>
            {USER_LINKS.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  [styles.link, isActive ? styles.linkActive : undefined].filter(Boolean).join(" ")
                }
              >
                {label}
              </NavLink>
            ))}
            <button type="button" className={styles.logoutButton} onClick={logout}>
              Sair
            </button>
          </>
        ) : (
          <NavLink
            to="/login"
            className={({ isActive }) =>
              [styles.link, isActive ? styles.linkActive : undefined].filter(Boolean).join(" ")
            }
          >
            Entrar
          </NavLink>
        )}
      </div>
    </nav>
  );
}
