import { NavLink } from "react-router-dom";

import { useAuth } from "@/contexts/AuthContext";

import { primaryNavigationLinks, userNavigationLinks } from "@/routes/config";

import styles from "./TopNav.module.css";

export function TopNav() {
  const { isAuthenticated, logout } = useAuth();

  return (
    <nav className={styles.nav}>
      <div className={styles.group}>
        <span className={styles.brand}>Disagua</span>
        {primaryNavigationLinks
          .filter((link) => (link.requiresAuth ? isAuthenticated : true))
          .map(({ to, label }) => (
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
            {userNavigationLinks.map(({ to, label }) => (
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
