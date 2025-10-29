import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable, TableColumn } from "@/components/ui/DataTable";
import { FormField } from "@/components/ui/FormField";
import { SelectInput } from "@/components/ui/SelectInput";
import { TableSkeleton } from "@/components/ui/TableSkeleton";
import { TextInput } from "@/components/ui/TextInput";
import { listConnections, createConnection, deleteConnection } from "@/services/connections";
import { listPartners, type PartnerRecord } from "@/services/partners";
import { listStores, type StoreRecord } from "@/services/stores";
import { useToast } from "@/contexts/ToastContext";

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
};

const FILTERS_STORAGE_KEY = "connect-page-filters";

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
  const [filters, setFilters] = useState(() => {
    if (typeof window === "undefined") {
      return { estado: "", cidade: "" };
    }
    try {
      const stored = window.localStorage.getItem(FILTERS_STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (typeof parsed === "object" && parsed) {
          return {
            estado: typeof parsed.estado === "string" ? parsed.estado : "",
            cidade: typeof parsed.cidade === "string" ? parsed.cidade : "",
          };
        }
      }
    } catch (err) {
      console.error("Não foi possível restaurar os filtros salvos", err);
    }
    return { estado: "", cidade: "" };
  });
  const [form, setForm] = useState<ConnectionForm>({ partnerId: "", storeId: "" });
  const [formErrors, setFormErrors] = useState<ConnectionFormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isBulkRemoving, setIsBulkRemoving] = useState(false);
  const { showSuccess, showError, showWarning } = useToast();

  const loadData = useCallback(() => {
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
        showError(message);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [showError]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    window.localStorage.setItem(FILTERS_STORAGE_KEY, JSON.stringify(filters));
  }, [filters]);

  const trimmedCity = filters.cidade.trim();
  const normalizedCity = trimmedCity.toLowerCase();

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

  const hasActiveFilters = Boolean(filters.estado || trimmedCity);

  const clearFilter = useCallback(
    (filterKey: "estado" | "cidade") => {
      setFilters((current) => ({ ...current, [filterKey]: "" }));
    },
    [],
  );

  const partnerResultLabel = useMemo(() => {
    const count = filteredPartners.length;
    return count === 1 ? "1 parceiro encontrado" : `${count} parceiros encontrados`;
  }, [filteredPartners.length]);

  const storeResultLabel = useMemo(() => {
    const count = filteredStores.length;
    return count === 1 ? "1 loja encontrada" : `${count} lojas encontradas`;
  }, [filteredStores.length]);

  const connectedPartnerIds = useMemo(() => new Set(connections.map((connection) => connection.partner?.id)), [connections]);
  const connectedStoreIds = useMemo(() => new Set(connections.map((connection) => connection.store?.id)), [connections]);

  const partnerColumns = useMemo<TableColumn<PartnerRecord>[]>(
    () => [
      { header: "Parceiro", accessor: "parceiro", sortable: true },
      {
        header: "Local",
        render: (partner) => `${partner.cidade} - ${partner.estado}`,
        sortable: true,
        sortValue: (partner) => `${partner.cidade ?? ""} ${partner.estado ?? ""}`,
        exportValue: (partner) => `${partner.cidade ?? ""} - ${partner.estado ?? ""}`,
      },
      {
        header: "Telefone",
        accessor: "telefone",
        sortable: true,
      },
      {
        header: "Ações",
        width: "140px",
        disableExport: true,
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
      { header: "Loja", accessor: "loja", sortable: true },
      {
        header: "Marca",
        accessor: "marca",
        sortable: true,
      },
      {
        header: "Local",
        render: (store) => `${store.municipio} - ${store.uf}`,
        sortable: true,
        sortValue: (store) => `${store.municipio ?? ""} ${store.uf ?? ""}`,
        exportValue: (store) => `${store.municipio ?? ""} - ${store.uf ?? ""}`,
      },
      {
        header: "Ações",
        width: "140px",
        disableExport: true,
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

  const handleDelete = useCallback(
    async (connectionId: number) => {
      if (!window.confirm("Deseja remover esta conexão?")) {
        return;
      }
      try {
        await deleteConnection(connectionId);
        setConnections((current) => current.filter((connection) => connection.id !== connectionId));
        setError(null);
        showSuccess("Conexão removida com sucesso.");
      } catch (err) {
        const message = err instanceof Error ? err.message : "Não foi possível remover a conexão.";
        setError(message);
        showError(message);
      }
    },
    [showError, showSuccess],
  );

  const connectionColumns = useMemo<TableColumn<ConnectionView>[]>(
    () => [
      {
        header: "Parceiro",
        render: (connection) => connection.partner?.parceiro ?? "—",
        sortable: true,
        sortValue: (connection) => connection.partner?.parceiro ?? "",
        exportValue: (connection) => connection.partner?.parceiro ?? "",
      },
      {
        header: "Loja",
        render: (connection) => connection.store?.loja ?? "—",
        sortable: true,
        sortValue: (connection) => connection.store?.loja ?? "",
        exportValue: (connection) => connection.store?.loja ?? "",
      },
      {
        header: "Marca",
        render: (connection) => connection.store?.marca ?? "—",
        sortable: true,
        sortValue: (connection) => connection.store?.marca ?? "",
        exportValue: (connection) => connection.store?.marca ?? "",
      },
      {
        header: "Ações",
        width: "140px",
        disableExport: true,
        render: (connection) => (
          <Button size="sm" variant="danger" type="button" onClick={() => handleDelete(connection.id)}>
            Desconectar
          </Button>
        ),
      },
    ],
    [handleDelete],
  );

  const handleBulkDisconnect = useCallback(
    async (selected: ConnectionView[], clearSelection: () => void) => {
      if (selected.length === 0) {
        return;
      }

      const confirmationMessage =
        selected.length === 1
          ? "Deseja remover a conexão selecionada?"
          : `Deseja remover ${selected.length} conexões selecionadas?`;
      if (!window.confirm(confirmationMessage)) {
        return;
      }

      setIsBulkRemoving(true);
      try {
        await Promise.all(selected.map((connection) => deleteConnection(connection.id)));
        const idsToRemove = new Set(selected.map((connection) => connection.id));
        setConnections((current) => current.filter((connection) => !idsToRemove.has(connection.id)));
        clearSelection();
        setError(null);
        const message =
          selected.length === 1
            ? "Conexão removida com sucesso."
            : `${selected.length} conexões removidas com sucesso.`;
        showSuccess(message);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Não foi possível remover as conexões.";
        setError(message);
        showError(message);
      } finally {
        setIsBulkRemoving(false);
      }
    },
    [showError, showSuccess],
  );

  const renderConnectionSelectionActions = useCallback(
    (selected: ConnectionView[], clearSelection: () => void) => (
      <Button
        size="sm"
        variant="danger"
        onClick={() => handleBulkDisconnect(selected, clearSelection)}
        isLoading={isBulkRemoving}
        loadingText="Removendo..."
      >
        {`Desconectar ${selected.length > 1 ? "selecionadas" : "selecionada"}`}
      </Button>
    ),
    [handleBulkDisconnect, isBulkRemoving],
  );

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormErrors({});

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
      showWarning("Essa conexão já existe.");
      return;
    }

    setIsSubmitting(true);
    try {
      await createConnection(partnerId, storeId);
      showSuccess("Conexão criada com sucesso.");
      setForm({ partnerId: "", storeId: "" });
      loadData();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível criar a conexão.";
      showError(message);
    } finally {
      setIsSubmitting(false);
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
        {hasActiveFilters ? (
          <div className={styles.activeFilters}>
            <span className={styles.activeFiltersLabel}>Filtros ativos:</span>
            <div className={styles.activeFiltersList}>
              {filters.estado ? (
                <button
                  type="button"
                  className={styles.filterChip}
                  onClick={() => clearFilter("estado")}
                  aria-label={`Remover filtro de UF ${filters.estado}`}
                >
                  <span className={styles.filterChipLabel}>UF: {filters.estado}</span>
                  <span className={styles.filterChipRemove} aria-hidden>
                    ×
                  </span>
                </button>
              ) : null}
              {trimmedCity ? (
                <button
                  type="button"
                  className={styles.filterChip}
                  onClick={() => clearFilter("cidade")}
                  aria-label={`Remover filtro de cidade ${trimmedCity}`}
                >
                  <span className={styles.filterChipLabel}>Cidade: {filters.cidade}</span>
                  <span className={styles.filterChipRemove} aria-hidden>
                    ×
                  </span>
                </button>
              ) : null}
            </div>
          </div>
        ) : null}
      </Card>

      <Card title="Criar conexão" subtitle="Selecione um parceiro e uma loja para vincular.">
        <form className={styles.form} onSubmit={handleSubmit}>
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
            <Button type="submit" isLoading={isSubmitting} loadingText="Conectando...">
              Criar conexão
            </Button>
          </div>
        </form>
      </Card>

      <div className={styles.grid}>
        <Card title="Parceiros disponíveis" subtitle="Selecione um parceiro para iniciar a conexão.">
          {isLoading ? <TableSkeleton columns={partnerColumns.length} /> : null}
          {!isLoading ? (
            <div className={styles.resultCount} role="status" aria-live="polite">
              {partnerResultLabel}
            </div>
          ) : null}
          {!isLoading && filteredPartners.length === 0 ? (
            <div className={styles.emptyState}>Nenhum parceiro encontrado para os filtros aplicados.</div>
          ) : null}
          {!isLoading && filteredPartners.length > 0 ? (
            <DataTable
              columns={partnerColumns}
              data={filteredPartners}
              keyExtractor={(partner) => partner.id.toString()}
              enableSorting
              enablePagination
              enableExport
              exportFileName="parceiros-disponiveis"
            />
          ) : null}
        </Card>

        <Card title="Lojas disponíveis" subtitle="Escolha uma loja para vincular ao parceiro selecionado.">
          {isLoading ? <TableSkeleton columns={storeColumns.length} /> : null}
          {!isLoading ? (
            <div className={styles.resultCount} role="status" aria-live="polite">
              {storeResultLabel}
            </div>
          ) : null}
          {!isLoading && filteredStores.length === 0 ? (
            <div className={styles.emptyState}>Nenhuma loja encontrada para os filtros aplicados.</div>
          ) : null}
          {!isLoading && filteredStores.length > 0 ? (
            <DataTable
              columns={storeColumns}
              data={filteredStores}
              keyExtractor={(store) => store.id.toString()}
              enableSorting
              enablePagination
              enableExport
              exportFileName="lojas-disponiveis"
            />
          ) : null}
        </Card>
      </div>

      <Card title="Conexões ativas" subtitle="Gerencie os vínculos já estabelecidos.">
        {isLoading ? <TableSkeleton columns={connectionColumns.length} /> : null}
        {!isLoading && connections.length === 0 && !error ? (
          <div className={styles.emptyState}>Nenhuma conexão ativa.</div>
        ) : null}
        {!isLoading && connections.length > 0 ? (
          <DataTable
            columns={connectionColumns}
            data={connections}
            keyExtractor={(connection) => connection.id}
            enableSorting
            enablePagination
            enableSelection
            selectionActions={renderConnectionSelectionActions}
            enableExport
            exportFileName="conexoes"
          />
        ) : null}
      </Card>
    </div>
  );
}
