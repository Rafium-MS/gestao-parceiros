import { Outlet } from "react-router-dom";

import { TopNav } from "@/components/TopNav";
import { Breadcrumbs } from "@/components/Breadcrumbs";

import styles from "./AppLayout.module.css";

export function AppLayout() {
  return (
    <div className={styles.wrapper}>
      <TopNav />
      <main className={styles.main}>
        <div className={styles.content}>
          <Breadcrumbs />
          <Outlet />
        </div>
      </main>
    </div>
  );
}
