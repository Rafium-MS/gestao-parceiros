import { PartnersTable } from "@/components/partners/PartnersTable";

export function PartnersPage() {
  return (
    <div>
      <header className="page-header">
        <h1>Parceiros</h1>
        <p>Cadastre, edite e acompanhe os parceiros ativos na plataforma.</p>
      </header>

      <PartnersTable />
    </div>
  );
}
