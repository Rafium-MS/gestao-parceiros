import { FormEvent, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable, TableColumn } from "@/components/ui/DataTable";
import { FormField } from "@/components/ui/FormField";
import { SelectInput } from "@/components/ui/SelectInput";
import { TextInput } from "@/components/ui/TextInput";
import { listConnections, createConnection, deleteConnection } from "@/services/connections";
import { listPartners, type PartnerRecord } from "@/services/partners";
import { listStores, type StoreRecord } from "@/services/stores";

import styles from "./ConnectPage.module.css";

type ConnectionView = {
  id: number;
  partner: PartnerRecord | undefined;
  store: StoreRecord | undefined;
};

type ConnectionForm = {
  partnerId: string;
  storeId: string;
};

type ConnectionFormErrors = {
  partnerId?: string;
  storeId?: string;
  global?: string;
};

const BRAZIL_STATES = [
  "",
  "AC",
  "AL",
  "AP",
  "AM",
  "BA",
  "CE",
  "DF",
  "ES",
  "GO",
  "MA",
  "MT",
  "MS",
  "MG",
  "PA",
  "PB",
  "PR",
  "PE",
  "PI",
  "RJ",
  "RN",
  "RS",
  "RO",
  "RR",
  "SC",
  "SP",
  "SE",
  "TO",
];

export function ConnectPage() {
  const [partners, setPartners] = useState<PartnerRecord[]>([]);
  const [stores, setStores] = useState<StoreRecord[]>([]);
  const [connections, setConnections] = useState<ConnectionView[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({ estado: "", cidade: "" });
  const [form, setForm] = useState<ConnectionForm>({ partnerId: "", storeId: "" });
  const [formErrors, setFormErrors] = useState<ConnectionFormErrors>({});
  const [formFeedback, setFormFeedback] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    setIsLoading(true);
    setError(null);
    Promise.all([listPartners(), listStores(), listConnections()])
      .then(([partnerList, storeList, connectionList]) => {
        setPartners(partnerList);
        setStores(storeList);
        setConnections(
          connectionList.map((connection) => ({
            id: connection.id,
            partner: partnerList.find((partner) => partner.id === connection.partner_id),
            store: storeList.find((store) => store.id === connection.store_id),
          })),
        );
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : "Não foi possível carregar as conexões.";
        setError(message);
        setPartners([]);
        setStores([]);
        setConnections([]);
      })
      .finally(() => {
        setIsLoading(false);
      });
  };

  const normalizedCity = filters.cidade.trim().toLowerCase();

  const filteredPartners = useMemo(() => {
    return partners.filter((partner) => {
      const matchesState = !filters.estado || partner.estado === filters.estado;
      const matchesCity = !normalizedCity || partner.cidade.toLowerCase().includes(normalizedCity);
      return matchesState && matchesCity;
    });
  }, [partners, filters.estado, normalizedCity]);

  const filteredStores = useMemo(() => {
    return stores.filter((store) => {
      const matchesState = !filters.estado || store.uf === filters.estado;
      const matchesCity = !normalizedCity || store.municipio.toLowerCase().includes(normalizedCity);
      return matchesState && matchesCity;
    });
  }, [stores, filters.estado, normalizedCity]);

  const connectedPartnerIds = useMemo(() => new Set(connections.map((connection) => connection.partner?.id)), [connections]);
  const connectedStoreIds = useMemo(() => new Set(connections.map((connection) => connection.store?.id)), [connections]);

  const partnerColumns = useMemo<TableColumn<PartnerRecord>[]>(
    () => [
      { header: "Parceiro", accessor: "parceiro" },
      {
        header: "Local",
        render: (partner) => `${partner.cidade} - ${partner.estado}`,
      },
      {
        header: "Telefone",
        accessor: "telefone",
      },
      {
        header: "Ações",
        width: "140px",
        render: (partner) => (
          <Button
            size="sm"
            type="button"
            onClick={() => setForm((current) => ({ ...current, partnerId: String(partner.id) }))}
            disabled={connectedPartnerIds.has(partner.id)}
            variant={connectedPartnerIds.has(partner.id) ? "ghost" : "secondary"}
          >
            {connectedPartnerIds.has(partner.id) ? "Conectado" : "Selecionar"}
          </Button>
        ),
      },
    ],
    [connectedPartnerIds],
  );

  const storeColumns = useMemo<TableColumn<StoreRecord>[]>(
    () => [
      { header: "Loja", accessor: "loja" },
      {
        header: "Marca",
        accessor: "marca",
      },
      {
        header: "Local",
        render: (store) => `${store.municipio} - ${store.uf}`,
      },
      {
        header: "Ações",
        width: "140px",
        render: (store) => (
          <Button
            size="sm"
            type="button"
            onClick={() => setForm((current) => ({ ...current, storeId: String(store.id) }))}
            disabled={connectedStoreIds.has(store.id)}
            variant={connectedStoreIds.has(store.id) ? "ghost" : "secondary"}
          >
            {connectedStoreIds.has(store.id) ? "Conectado" : "Selecionar"}
          </Button>
        ),
      },
    ],
    [connectedStoreIds],
  );

  const connectionColumns = useMemo<TableColumn<ConnectionView>[]>(
    () => [
      {
        header: "Parceiro",
        render: (connection) => connection.partner?.parceiro ?? "—",
      },
      {
        header: "Loja",
        render: (connection) => connection.store?.loja ?? "—",
      },
      {
        header: "Marca",
        render: (connection) => connection.store?.marca ?? "—",
      },
      {
        header: "Ações",
        width: "140px",
        render: (connection) => (
          <Button size="sm" variant="danger" type="button" onClick={() => handleDelete(connection.id)}>
            Desconectar
          </Button>
        ),
      },
    ],
    [],
  );

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormErrors({});
    setFormFeedback(null);

    const errors: ConnectionFormErrors = {};
    if (!form.partnerId) {
      errors.partnerId = "Selecione um parceiro.";
    }
    if (!form.storeId) {
      errors.storeId = "Selecione uma loja.";
    }

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    const partnerId = Number(form.partnerId);
    const storeId = Number(form.storeId);
    const alreadyExists = connections.some(
      (connection) => connection.partner?.id === partnerId && connection.store?.id === storeId,
    );
    if (alreadyExists) {
      setFormErrors({ global: "Essa conexão já existe." });
      return;
    }

    setIsSubmitting(true);
    try {
      await createConnection(partnerId, storeId);
      setFormFeedback("Conexão criada com sucesso.");
      setForm({ partnerId: "", storeId: "" });
      loadData();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível criar a conexão.";
      setFormErrors({ global: message });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (connectionId: number) => {
    if (!window.confirm("Deseja remover esta conexão?")) {
      return;
    }
    try {
      await deleteConnection(connectionId);
      loadData();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível remover a conexão.";
      setError(message);
    }
  };

  return (
    <div className={styles.container}>
      <header className="page-header">
        <h1>Conectar Parceiros e Lojas</h1>
        <p>Disponibilize oportunidades de venda criando relações entre parceiros e marcas.</p>
      </header>

      <Card title="Filtros" subtitle="Refine a visualização de parceiros e lojas disponíveis.">
        <div className={styles.filterGrid}>
          <FormField label="UF" htmlFor="filter-state">
            <SelectInput
              id="filter-state"
              value={filters.estado}
              onChange={(event) => setFilters((current) => ({ ...current, estado: event.target.value }))}
            >
              <option value="">Todas</option>
              {BRAZIL_STATES.filter(Boolean).map((uf) => (
                <option key={uf} value={uf}>
                  {uf}
                </option>
              ))}
            </SelectInput>
          </FormField>
          <FormField label="Cidade" htmlFor="filter-city">
            <TextInput
              id="filter-city"
              value={filters.cidade}
              onChange={(event) => setFilters((current) => ({ ...current, cidade: event.target.value }))}
              placeholder="Digite para filtrar"
            />
          </FormField>
        </div>
      </Card>

      <Card title="Criar conexão" subtitle="Selecione um parceiro e uma loja para vincular.">
        <form className={styles.form} onSubmit={handleSubmit}>
          {formErrors.global ? <div className={styles.errorMessage}>{formErrors.global}</div> : null}
          {formFeedback ? (
            <div className={styles.successMessage} role="status" aria-live="polite">
              {formFeedback}
            </div>
          ) : null}

          <div className={styles.formRow}>
            <FormField label="Parceiro" htmlFor="connection-partner" error={formErrors.partnerId}>
              <SelectInput
                id="connection-partner"
                value={form.partnerId}
                onChange={(event) => setForm((current) => ({ ...current, partnerId: event.target.value }))}
                hasError={Boolean(formErrors.partnerId)}
              >
                <option value="">Selecione</option>
                {partners.map((partner) => (
                  <option key={partner.id} value={partner.id}>
                    {partner.parceiro} — {partner.cidade}/{partner.estado}
                  </option>
                ))}
              </SelectInput>
            </FormField>

            <FormField label="Loja" htmlFor="connection-store" error={formErrors.storeId}>
              <SelectInput
                id="connection-store"
                value={form.storeId}
                onChange={(event) => setForm((current) => ({ ...current, storeId: event.target.value }))}
                hasError={Boolean(formErrors.storeId)}
              >
                <option value="">Selecione</option>
                {stores.map((store) => (
                  <option key={store.id} value={store.id}>
                    {store.loja} — {store.municipio}/{store.uf}
                  </option>
                ))}
              </SelectInput>
            </FormField>
          </div>

          <div className={styles.formActions}>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Conectando..." : "Criar conexão"}
            </Button>
          </div>
        </form>
      </Card>

      <div className={styles.grid}>
        <Card title="Parceiros disponíveis" subtitle="Selecione um parceiro para iniciar a conexão.">
          {isLoading ? <div className={styles.loadingMessage}>Carregando parceiros...</div> : null}
          {!isLoading && filteredPartners.length === 0 ? (
            <div className={styles.emptyState}>Nenhum parceiro encontrado para os filtros aplicados.</div>
          ) : null}
          {!isLoading && filteredPartners.length > 0 ? (
            <DataTable
              columns={partnerColumns}
              data={filteredPartners}
              keyExtractor={(partner) => partner.id.toString()}
            />
          ) : null}
        </Card>

        <Card title="Lojas disponíveis" subtitle="Escolha uma loja para vincular ao parceiro selecionado.">
          {isLoading ? <div className={styles.loadingMessage}>Carregando lojas...</div> : null}
          {!isLoading && filteredStores.length === 0 ? (
            <div className={styles.emptyState}>Nenhuma loja encontrada para os filtros aplicados.</div>
          ) : null}
          {!isLoading && filteredStores.length > 0 ? (
            <DataTable columns={storeColumns} data={filteredStores} keyExtractor={(store) => store.id.toString()} />
          ) : null}
        </Card>
      </div>

      <Card title="Conexões ativas" subtitle="Gerencie os vínculos já estabelecidos.">
        {error ? <div className={styles.errorMessage}>{error}</div> : null}
        {isLoading ? <div className={styles.loadingMessage}>Carregando conexões...</div> : null}
        {!isLoading && connections.length === 0 && !error ? (
          <div className={styles.emptyState}>Nenhuma conexão ativa.</div>
        ) : null}
        {!isLoading && connections.length > 0 ? (
          <DataTable columns={connectionColumns} data={connections} keyExtractor={(connection) => connection.id} />
        ) : null}
      </Card>
    </div>
  );
}
