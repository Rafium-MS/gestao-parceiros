import { useAuth } from "@/contexts/AuthContext";

export function AccountPage() {
  const { logout } = useAuth();

  return (
    <div className="page-content">
      <header className="page-header">
        <h1>Minha Conta</h1>
        <p>Atualize dados pessoais e redefina a senha de acesso ao painel.</p>
      </header>
      <section>
        <p>
          Em paralelo à página <code>account.html</code>, esta rota receberá formulários protegidos e validadores. O
          botão abaixo permite testar o fluxo de encerramento de sessão enquanto a integração com o backend não é
          concluída.
        </p>
        <button type="button" onClick={logout}>
          Encerrar sessão
        </button>
      </section>
    </div>
  );
}
