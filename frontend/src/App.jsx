import React from 'react';
import { Link, Routes, Route } from 'react-router-dom';
import './App.css';
import ParceirosPage from './components/Parceiros';

// Placeholder components
const HomePage = () => <h2>Página Inicial</h2>;
const LojasPage = () => <h2>Gerenciamento de Lojas</h2>;
const ComprovantesPage = () => <h2>Gerenciamento de Comprovantes</h2>;
const AssociacoesPage = () => <h2>Gerenciamento de Associações</h2>;
const RelatoriosPage = () => <h2>Relatórios</h2>;


function App() {
  return (
    <>
      <nav>
        <ul>
          <li><Link to="/">Início</Link></li>
          <li><Link to="/parceiros">Parceiros</Link></li>
          <li><Link to="/lojas">Lojas</Link></li>
          <li><Link to="/comprovantes">Comprovantes</Link></li>
          <li><Link to="/associacoes">Associações</Link></li>
          <li><Link to="/relatorios">Relatórios</Link></li>
        </ul>
      </nav>

      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/parceiros" element={<ParceirosPage />} />
          <Route path="/lojas" element={<LojasPage />} />
          <Route path="/comprovantes" element={<ComprovantesPage />} />
          <Route path="/associacoes" element={<AssociacoesPage />} />
          <Route path="/relatorios" element={<RelatoriosPage />} />
        </Routes>
      </main>
    </>
  );
}

export default App;
