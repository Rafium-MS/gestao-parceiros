import { Link } from "react-router-dom";

const QUICK_LINKS = [
  { to: "/parceiros", title: "Parceiros", description: "Cadastre parceiros e acompanhe seus dados atualizados." },
  { to: "/lojas", title: "Lojas", description: "Gerencie marcas, lojas e políticas comerciais." },
  { to: "/conectar", title: "Conectar", description: "Relacione parceiros e lojas para criar oportunidades." },
  { to: "/comprovantes", title: "Comprovantes", description: "Faça upload e organize comprovantes de pagamento." },
  { to: "/relatorios", title: "Relatórios", description: "Visualize métricas detalhadas de marcas e volume." },
  { to: "/usuarios", title: "Usuários", description: "Controle o acesso da equipe ao portal de parceiros." },
];

export function DashboardPage() {
  return (
    <div>
      <header>
        <h1>Bem-vindo!</h1>
        <p>Gerencie parceiros, lojas, conexões e relatórios em um só lugar.</p>
      </header>
      <section>
        <div className="quick-links">
          {QUICK_LINKS.map((item) => (
            <Link key={item.to} to={item.to} className="quick-link">
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
