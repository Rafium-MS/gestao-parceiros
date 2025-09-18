import React from 'react';
import { Link, Routes, Route, useLocation } from 'react-router-dom';
import './App.css';
import ParceirosPage from './components/Parceiros';
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";

// Placeholder components
const HomePage = () => <h2 className="text-2xl font-bold">Página Inicial</h2>;
const LojasPage = () => <h2 className="text-2xl font-bold">Gerenciamento de Lojas</h2>;
const ComprovantesPage = () => <h2 className="text-2xl font-bold">Gerenciamento de Comprovantes</h2>;
const AssociacoesPage = () => <h2 className="text-2xl font-bold">Gerenciamento de Associações</h2>;
const RelatoriosPage = () => <h2 className="text-2xl font-bold">Relatórios</h2>;

const navLinks = [
  { path: '/', label: 'Início' },
  { path: '/parceiros', label: 'Parceiros' },
  { path: '/lojas', label: 'Lojas' },
  { path: '/comprovantes', label: 'Comprovantes' },
  { path: '/associacoes', label: 'Associações' },
  { path: '/relatorios', label: 'Relatórios' },
];

function App() {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b">
        <div className="container mx-auto flex h-16 items-center justify-center px-4">
          <NavigationMenu>
            <NavigationMenuList>
              {navLinks.map((navLink) => (
                <NavigationMenuItem key={navLink.path}>
                  <Link to={navLink.path}>
                    <NavigationMenuLink
                      className={navigationMenuTriggerStyle()}
                      active={location.pathname === navLink.path}
                    >
                      {navLink.label}
                    </NavigationMenuLink>
                  </Link>
                </NavigationMenuItem>
              ))}
            </NavigationMenuList>
          </NavigationMenu>
        </div>
      </header>

      <main className="container mx-auto p-4 md:p-6">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/parceiros" element={<ParceirosPage />} />
          <Route path="/lojas" element={<LojasPage />} />
          <Route path="/comprovantes" element={<ComprovantesPage />} />
          <Route path="/associacoes" element={<AssociacoesPage />} />
          <Route path="/relatorios" element={<RelatoriosPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
