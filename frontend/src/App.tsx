import { Suspense } from "react";
import { BrowserRouter, useRoutes } from "react-router-dom";

import { AuthProvider } from "@/contexts/AuthContext";
import { ToastProvider } from "@/contexts/ToastContext";
import { appRoutes } from "@/routes/config";

function AppRoutes() {
  return useRoutes(appRoutes);
}

function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <BrowserRouter>
          <Suspense fallback={<div className="page-loading">Carregando interface...</div>}>
            <AppRoutes />
          </Suspense>
        </BrowserRouter>
      </AuthProvider>
    </ToastProvider>
  );
}

export default App;
