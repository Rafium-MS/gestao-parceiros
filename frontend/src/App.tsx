import { useEffect, useState } from "react";
import { env } from "@/config/env";
import { fetchStatus } from "@/services/status";

function App() {
  const [message, setMessage] = useState("Carregando informações da API...");

  useEffect(() => {
    let mounted = true;
    fetchStatus()
      .then((apiMessage) => {
        if (mounted) {
          setMessage(apiMessage);
        }
      })
      .catch(() => {
        if (mounted) {
          setMessage(
            "Não foi possível conectar à API. Verifique se o backend Flask está em execução na URL configurada.",
          );
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <main className="app">
      <header className="app__header">
        <h1>Gestão de Parceiros</h1>
        <p className="app__subtitle">
          Frontend React configurado com Vite, TypeScript, ESLint, Prettier e aliases de importação.
        </p>
      </header>
      <section className="app__content">
        <p>
          <strong>API base:</strong> <code>{env.apiBaseUrl}</code>
        </p>
        <p>
          <strong>Status:</strong> {message}
        </p>
      </section>
    </main>
  );
}

export default App;
