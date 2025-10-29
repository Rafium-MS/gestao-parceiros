import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AuthProvider } from "@/contexts/AuthContext";
import { ToastProvider } from "@/contexts/ToastContext";
import { AppLayout } from "@/layouts/AppLayout";
import { AccountPage } from "@/pages/AccountPage";
import { ConnectPage } from "@/pages/ConnectPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { LoginPage } from "@/pages/LoginPage";
import { PartnersPage } from "@/pages/PartnersPage";
import { ReceiptsPage } from "@/pages/ReceiptsPage";
import { ReportsPage } from "@/pages/ReportsPage";
import { StoresPage } from "@/pages/StoresPage";
import { UsersPage } from "@/pages/UsersPage";
import { ProtectedRoute } from "@/routes/ProtectedRoute";

function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <BrowserRouter>
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
        </BrowserRouter>
      </AuthProvider>
    </ToastProvider>
  );
}

export default App;
