import { Suspense, lazy } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AuthProvider } from "@/contexts/AuthContext";
import { ToastProvider } from "@/contexts/ToastContext";
import { AppLayout } from "@/layouts/AppLayout";
import { ProtectedRoute } from "@/routes/ProtectedRoute";

const DashboardPage = lazy(() =>
  import("@/pages/DashboardPage").then((module) => ({ default: module.DashboardPage })),
);
const PartnersPage = lazy(() =>
  import("@/pages/PartnersPage").then((module) => ({ default: module.PartnersPage })),
);
const StoresPage = lazy(() =>
  import("@/pages/StoresPage").then((module) => ({ default: module.StoresPage })),
);
const ReceiptsPage = lazy(() =>
  import("@/pages/ReceiptsPage").then((module) => ({ default: module.ReceiptsPage })),
);
const ReportsPage = lazy(() =>
  import("@/pages/ReportsPage").then((module) => ({ default: module.ReportsPage })),
);
const UsersPage = lazy(() =>
  import("@/pages/UsersPage").then((module) => ({ default: module.UsersPage })),
);
const AccountPage = lazy(() =>
  import("@/pages/AccountPage").then((module) => ({ default: module.AccountPage })),
);
const ConnectPage = lazy(() =>
  import("@/pages/ConnectPage").then((module) => ({ default: module.ConnectPage })),
);
const LoginPage = lazy(() =>
  import("@/pages/LoginPage").then((module) => ({ default: module.LoginPage })),
);

function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <BrowserRouter>
          <Suspense fallback={<div className="page-loading">Carregando interface...</div>}>
            <Routes>
              <Route path="/login" element={<LoginPage />} />

              <Route element={<AppLayout />}>
                <Route path="/conectar" element={<ConnectPage />} />
              </Route>

              <Route element={<ProtectedRoute />}>
                <Route element={<AppLayout />}>
                  <Route index element={<DashboardPage />} />
                  <Route path="/parceiros" element={<PartnersPage />} />
                  <Route path="/lojas" element={<StoresPage />} />
                  <Route path="/comprovantes" element={<ReceiptsPage />} />
                  <Route path="/relatorios" element={<ReportsPage />} />
                  <Route path="/usuarios" element={<UsersPage />} />
                  <Route path="/account" element={<AccountPage />} />
                </Route>
              </Route>

              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </AuthProvider>
    </ToastProvider>
  );
}

export default App;
