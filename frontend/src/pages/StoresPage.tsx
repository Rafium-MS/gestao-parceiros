import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable, TableColumn } from "@/components/ui/DataTable";
import { FormField } from "@/components/ui/FormField";
import { Modal } from "@/components/ui/Modal";
import { SelectInput } from "@/components/ui/SelectInput";
import { TableSkeleton } from "@/components/ui/TableSkeleton";
import { TextInput } from "@/components/ui/TextInput";
import {
  createBrand,
  deleteBrand,
  listBrands,
  type BrandPayload,
  type BrandRecord,
  type BrandStoreImportSummary,
  updateBrand,
} from "@/services/brands";
import {
  createStore,
  deleteStore,
  listStores,
  type StorePayload,
  type StoreRecord,
  updateStore,
} from "@/services/stores";
import { formatCurrency } from "@/utils/formatters";
import { useToast } from "@/contexts/ToastContext";
import { useConfirmDialog } from "@/hooks/useConfirmDialog";
import { StoresImportModal } from "@/components/stores/StoresImportModal";

import styles from "./StoresPage.module.css";

type SummaryMetric = {
  label: string;
  value: string;
  helper?: string;
  icon: string;
};

type BrandFormErrors = {
  marca?: string;
};

type StoreFormErrors = {
  marca_id?: string;
  loja?: string;
  local_entrega?: string;
  municipio?: string;
  uf?: string;
};

type FormMode = "create" | "edit";

type StoreFormState = {
  marca_id: string;
  loja: string;
  cod_disagua: string;
  local_entrega: string;
  endereco: string;
  municipio: string;
  uf: string;
  valor_20l: string;
  valor_10l: string;
  valor_1500ml: string;
  valor_cx_copo: string;
  valor_vasilhame: string;
};

const BRAZIL_STATES = [
  { value: "AC", label: "Acre" },
  { value: "AL", label: "Alagoas" },
  { value: "AP", label: "Amapá" },
  { value: "AM", label: "Amazonas" },
  { value: "BA", label: "Bahia" },
  { value: "CE", label: "Ceará" },
  { value: "DF", label: "Distrito Federal" },
  { value: "ES", label: "Espírito Santo" },
  { value: "GO", label: "Goiás" },
  { value: "MA", label: "Maranhão" },
  { value: "MT", label: "Mato Grosso" },
  { value: "MS", label: "Mato Grosso do Sul" },
  { value: "MG", label: "Minas Gerais" },
  { value: "PA", label: "Pará" },
  { value: "PB", label: "Paraíba" },
  { value: "PR", label: "Paraná" },
  { value: "PE", label: "Pernambuco" },
  { value: "PI", label: "Piauí" },
  { value: "RJ", label: "Rio de Janeiro" },
  { value: "RN", label: "Rio Grande do Norte" },
  { value: "RS", label: "Rio Grande do Sul" },
  { value: "RO", label: "Rondônia" },
  { value: "RR", label: "Roraima" },
  { value: "SC", label: "Santa Catarina" },
  { value: "SP", label: "São Paulo" },
  { value: "SE", label: "Sergipe" },
  { value: "TO", label: "Tocantins" },
];

const STORE_PRICE_FIELDS = [
  { key: "valor_20l", label: "Garrafa 20L" },
  { key: "valor_10l", label: "Garrafa 10L" },
  { key: "valor_1500ml", label: "Garrafa 1500ml" },
  { key: "valor_cx_copo", label: "Caixa de copos" },
  { key: "valor_vasilhame", label: "Vasilhame" },
] as const satisfies Array<{ key: keyof StoreFormState; label: string }>;

const defaultStoreForm: StoreFormState = {
  marca_id: "",
  loja: "",
  cod_disagua: "",
  local_entrega: "",
  endereco: "",
  municipio: "",
  uf: "",
  valor_20l: "0",
  valor_10l: "0",
  valor_1500ml: "0",
  valor_cx_copo: "0",
  valor_vasilhame: "0",
};

function parseCurrency(value: string) {
  const parsed = Number.parseFloat(value.replace(",", "."));
  if (Number.isNaN(parsed)) {
    return 0;
  }
  return parsed;
}

export function StoresPage() {
  const [brands, setBrands] = useState<BrandRecord[]>([]);
  const [stores, setStores] = useState<StoreRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [brandForm, setBrandForm] = useState<BrandPayload>({ marca: "", cod_disagua: "" });
  const [brandErrors, setBrandErrors] = useState<BrandFormErrors>({});
  const [brandMode, setBrandMode] = useState<FormMode>("create");
  const [editingBrandId, setEditingBrandId] = useState<number | null>(null);
  const [isSubmittingBrand, setIsSubmittingBrand] = useState(false);
  const [isBrandModalOpen, setIsBrandModalOpen] = useState(false);
  const [storeForm, setStoreForm] = useState<StoreFormState>(defaultStoreForm);
  const [storeErrors, setStoreErrors] = useState<StoreFormErrors>({});
  const [storeMode, setStoreMode] = useState<FormMode>("create");
  const [editingStoreId, setEditingStoreId] = useState<number | null>(null);
  const [isSubmittingStore, setIsSubmittingStore] = useState(false);
  const [isStoreModalOpen, setIsStoreModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"brands" | "stores">("brands");
  const [expandedBrands, setExpandedBrands] = useState<Set<number>>(new Set());
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
  const { showSuccess, showError } = useToast();
  const { confirm: requestConfirmation, dialog: confirmDialog } = useConfirmDialog();

  const loadAll = useCallback(() => {
    setIsLoading(true);
    setError(null);

    return Promise.all([listBrands(), listStores()])
      .then(([brandList, storeList]) => {
        setBrands(brandList);
        setStores(storeList);
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : "Não foi possível carregar marcas e lojas.";
        setError(message);
        setBrands([]);
        setStores([]);
        showError(message);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [showError]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  const handleOpenImport = () => {
    setIsImportModalOpen(true);
  };

  const handleCloseImport = useCallback(() => {
    setIsImportModalOpen(false);
  }, []);

  const handleImportCompleted = useCallback(
    async (result: BrandStoreImportSummary) => {
      await loadAll();

      const parts: string[] = [];
      if (result.created_brands > 0) {
        parts.push(
          `${result.created_brands} marca${result.created_brands > 1 ? "s" : ""} nova${
            result.created_brands > 1 ? "s" : ""
          }`,
        );
      }
      if (result.updated_brands > 0) {
        parts.push(
          `${result.updated_brands} marca${result.updated_brands > 1 ? "s" : ""} atualizada${
            result.updated_brands > 1 ? "s" : ""
          }`,
        );
      }
      if (result.created_stores > 0) {
        parts.push(
          `${result.created_stores} loja${result.created_stores > 1 ? "s" : ""} nova${
            result.created_stores > 1 ? "s" : ""
          }`,
        );
      }
      if (result.updated_stores > 0) {
        parts.push(
          `${result.updated_stores} loja${result.updated_stores > 1 ? "s" : ""} atualizada${
            result.updated_stores > 1 ? "s" : ""
          }`,
        );
      }

      const summaryMessage = parts.length > 0 ? parts.join(", ") : "nenhuma alteração aplicada";
      const errorNote =
        result.error_count > 0
          ? ` (houve ${result.error_count} erro${result.error_count > 1 ? "s" : ""})`
          : "";

      showSuccess(`Importação concluída: ${summaryMessage}${errorNote}.`);
    },
    [loadAll, showSuccess],
  );

  const metrics = useMemo<SummaryMetric[]>(() => {
    const totalBrands = brands.length;
    const totalStores = stores.length;
    const avgStoresPerBrand = totalBrands > 0 ? totalStores / totalBrands : 0;
    const topBrand = brands.reduce<BrandRecord | null>((prev, brand) => {
      if (!prev || brand.store_count > prev.store_count) {
        return brand;
      }
      return prev;
    }, null);

    const totalInvestimento = stores.reduce((total, store) => {
      return (
        total +
        store.valor_20l +
        store.valor_10l +
        store.valor_1500ml +
        store.valor_cx_copo +
        store.valor_vasilhame
      );
    }, 0);

    return [
      {
        label: "Marcas ativas",
        value: totalBrands.toString(),
        helper: topBrand ? `Maior portfólio: ${topBrand.marca}` : "Cadastre marcas para começar.",
        icon: "🏷️",
      },
      {
        label: "Lojas cadastradas",
        value: totalStores.toString(),
        helper:
          totalBrands > 0
            ? `${avgStoresPerBrand.toFixed(1)} lojas por marca`
            : "Associe lojas às marcas cadastradas.",
        icon: "🏬",
      },
      {
        label: "Ticket médio por loja",
        value: totalStores > 0 ? formatCurrency(totalInvestimento / totalStores) : "R$ 0,00",
        helper: "Soma dos valores praticados por loja.",
        icon: "💰",
      },
    ];
  }, [brands, stores]);

  const storeColumns = useMemo<TableColumn<StoreRecord>[]>(
    () => [
      { header: "Marca", accessor: "marca" },
      { header: "Loja", accessor: "loja" },
      {
        header: "Município",
        render: (store) => `${store.municipio} - ${store.uf}`,
      },
      {
        header: "Local de entrega",
        render: (store) => store.local_entrega,
      },
      {
        header: "Mix total",
        align: "right",
        render: (store) =>
          formatCurrency(
            store.valor_20l +
              store.valor_10l +
              store.valor_1500ml +
              store.valor_cx_copo +
              store.valor_vasilhame,
          ),
      },
    ],
    [],
  );

  const resetBrandForm = () => {
    setBrandForm({ marca: "", cod_disagua: "" });
    setBrandMode("create");
    setEditingBrandId(null);
    setBrandErrors({});
  };

  const resetStoreForm = () => {
    setStoreForm({ ...defaultStoreForm });
    setStoreMode("create");
    setEditingStoreId(null);
    setStoreErrors({});
  };

  const handleCloseBrandModal = () => {
    setIsBrandModalOpen(false);
    resetBrandForm();
  };

  const handleCloseStoreModal = () => {
    setIsStoreModalOpen(false);
    resetStoreForm();
  };

  const handleBrandSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setBrandErrors({});

    if (!brandForm.marca?.trim()) {
      setBrandErrors({ marca: "Informe o nome da marca." });
      return;
    }

    setIsSubmittingBrand(true);
    try {
      if (brandMode === "create") {
        await createBrand({
          marca: brandForm.marca.trim(),
          cod_disagua: brandForm.cod_disagua?.trim() || undefined,
        });
        showSuccess("Marca cadastrada com sucesso.");
      } else if (editingBrandId !== null) {
        await updateBrand(editingBrandId, {
          marca: brandForm.marca.trim(),
          cod_disagua: brandForm.cod_disagua?.trim() || null,
        });
        showSuccess("Marca atualizada com sucesso.");
      }
      await loadAll();
      handleCloseBrandModal();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível salvar a marca.";
      showError(message);
    } finally {
      setIsSubmittingBrand(false);
    }
  };

  const startEditBrand = (brand: BrandRecord) => {
    setBrandForm({ marca: brand.marca, cod_disagua: brand.cod_disagua ?? "" });
    setBrandMode("edit");
    setEditingBrandId(brand.id);
    setBrandErrors({});
    setIsBrandModalOpen(true);
  };

  const handleDeleteBrand = async (brand: BrandRecord) => {
    const confirmed = await requestConfirmation({
      title: "Remover marca",
      description: `Tem certeza de que deseja excluir a marca ${brand.marca}? Essa ação não poderá ser desfeita.`,
      confirmLabel: "Excluir marca",
      confirmVariant: "danger",
      tone: "danger",
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteBrand(brand.id);
      await loadAll();
      showSuccess("Marca excluída com sucesso.");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível excluir a marca.";
      showError(message);
    }
  };

  const handleStoreSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setStoreErrors({});

    const errors: StoreFormErrors = {};
    if (!storeForm.marca_id) {
      errors.marca_id = "Selecione uma marca.";
    }
    if (!storeForm.loja.trim()) {
      errors.loja = "Informe o nome da loja.";
    }
    if (!storeForm.local_entrega.trim()) {
      errors.local_entrega = "Informe o local de entrega.";
    }
    if (!storeForm.municipio.trim()) {
      errors.municipio = "Informe o município.";
    }
    if (!storeForm.uf) {
      errors.uf = "Selecione a UF.";
    }

    if (Object.keys(errors).length > 0) {
      setStoreErrors(errors);
      return;
    }

    const payload: StorePayload = {
      marca_id: Number(storeForm.marca_id),
      loja: storeForm.loja.trim(),
      cod_disagua: storeForm.cod_disagua?.trim() || undefined,
      local_entrega: storeForm.local_entrega.trim(),
      endereco: storeForm.endereco?.trim() || undefined,
      municipio: storeForm.municipio.trim(),
      uf: storeForm.uf,
      valor_20l: parseCurrency(storeForm.valor_20l),
      valor_10l: parseCurrency(storeForm.valor_10l),
      valor_1500ml: parseCurrency(storeForm.valor_1500ml),
      valor_cx_copo: parseCurrency(storeForm.valor_cx_copo),
      valor_vasilhame: parseCurrency(storeForm.valor_vasilhame),
    };

    setIsSubmittingStore(true);
    try {
      if (storeMode === "create") {
        await createStore(payload);
        showSuccess("Loja cadastrada com sucesso.");
      } else if (editingStoreId !== null) {
        await updateStore(editingStoreId, payload);
        showSuccess("Loja atualizada com sucesso.");
      }
      await loadAll();
      handleCloseStoreModal();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível salvar a loja.";
      showError(message);
    } finally {
      setIsSubmittingStore(false);
    }
  };

  const startEditStore = (store: StoreRecord) => {
    setStoreForm({
      marca_id: String(store.marca_id),
      loja: store.loja ?? "",
      cod_disagua: store.cod_disagua ?? "",
      local_entrega: store.local_entrega ?? "",
      endereco: store.endereco ?? "",
      municipio: store.municipio ?? "",
      uf: store.uf ?? "",
      valor_20l: String(store.valor_20l ?? 0),
      valor_10l: String(store.valor_10l ?? 0),
      valor_1500ml: String(store.valor_1500ml ?? 0),
      valor_cx_copo: String(store.valor_cx_copo ?? 0),
      valor_vasilhame: String(store.valor_vasilhame ?? 0),
    });
    setStoreMode("edit");
    setEditingStoreId(store.id);
    setStoreErrors({});
    setIsStoreModalOpen(true);
  };

  const handleDeleteStore = async (store: StoreRecord) => {
    const confirmed = await requestConfirmation({
      title: "Remover loja",
      description: `Tem certeza de que deseja excluir a loja ${store.loja}? Essa ação não poderá ser desfeita.`,
      confirmLabel: "Excluir loja",
      confirmVariant: "danger",
      tone: "danger",
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteStore(store.id);
      await loadAll();
      showSuccess("Loja excluída com sucesso.");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível excluir a loja.";
      showError(message);
    }
  };

  const handleAddStoreToBrand = (brandId: number) => {
    setStoreForm({ ...defaultStoreForm, marca_id: String(brandId) });
    setStoreMode("create");
    setEditingStoreId(null);
    setStoreErrors({});
    setActiveTab("stores");
    setIsStoreModalOpen(true);
  };

  const toggleBrand = (brandId: number, open: boolean) => {
    setExpandedBrands((current) => {
      const next = new Set(current);
      if (open) {
        next.add(brandId);
      } else {
        next.delete(brandId);
      }
      return next;
    });
  };

  const orderedBrands = useMemo(
    () => [...brands].sort((a, b) => a.marca.localeCompare(b.marca, "pt-BR")),
    [brands],
  );

  const handleOpenCreateBrand = () => {
    resetBrandForm();
    setIsBrandModalOpen(true);
  };

  const handleOpenCreateStore = () => {
    resetStoreForm();
    setActiveTab("stores");
    setIsStoreModalOpen(true);
  };

  const handlePriceChange = (key: (typeof STORE_PRICE_FIELDS)[number]["key"], value: string) => {
    setStoreForm((current) => ({ ...current, [key]: value }));
  };

  const brandTabId = "brands-tab";
  const brandPanelId = "brands-panel";
  const storeTabId = "stores-tab";
  const storePanelId = "stores-panel";

  const isBrandFormValid = Boolean(brandForm.marca?.trim());
  const isStoreFormValid =
    Boolean(storeForm.marca_id) &&
    storeForm.loja.trim().length > 0 &&
    storeForm.local_entrega.trim().length > 0 &&
    storeForm.municipio.trim().length > 0 &&
    storeForm.uf.trim().length > 0;

  return (
    <>
      {confirmDialog}
      <div className={styles.container}>
        <header className="page-header">
          <h1>Marcas e Lojas</h1>
          <p>Gerencie marcas, lojas e políticas comerciais com base nos dados registrados pelo backend.</p>
        </header>

        {error ? <div className={styles.errorMessage}>{error}</div> : null}

        <section className={styles.summary} aria-label="Indicadores gerais" aria-live="polite">
          {metrics.map((metric) => (
            <article key={metric.label} className={styles.summaryCard}>
              <span className={styles.summaryIcon} aria-hidden="true">
                {metric.icon}
              </span>
              <div className={styles.summaryContent}>
                <span className={styles.summaryLabel}>{metric.label}</span>
                <strong className={styles.summaryValue}>{metric.value}</strong>
                {metric.helper ? <span className={styles.summaryHelper}>{metric.helper}</span> : null}
              </div>
            </article>
          ))}
        </section>

        <nav className={styles.tabs} aria-label="Seções de gerenciamento" role="tablist">
          <button
            id={brandTabId}
            type="button"
            role="tab"
            aria-controls={brandPanelId}
            aria-selected={activeTab === "brands"}
            tabIndex={activeTab === "brands" ? 0 : -1}
            data-active={activeTab === "brands" ? "true" : undefined}
            onClick={() => setActiveTab("brands")}
          >
            Marcas
          </button>
          <button
            id={storeTabId}
            type="button"
            role="tab"
            aria-controls={storePanelId}
            aria-selected={activeTab === "stores"}
            tabIndex={activeTab === "stores" ? 0 : -1}
            data-active={activeTab === "stores" ? "true" : undefined}
            onClick={() => setActiveTab("stores")}
          >
            Lojas
          </button>
        </nav>

        <section
          id={brandPanelId}
          role="tabpanel"
          aria-labelledby={brandTabId}
          hidden={activeTab !== "brands"}
          className={styles.tabPanel}
        >
          <Card
            title="Portfólio de marcas"
            subtitle="Cadastre marcas e visualize as lojas vinculadas a cada portfólio."
            actions={
              <div className={styles.cardActions}>
                <Button type="button" variant="secondary" onClick={handleOpenImport}>
                  Importar planilha
                </Button>
                <Button type="button" onClick={handleOpenCreateBrand}>
                  Nova marca
                </Button>
              </div>
            }
          >
            <p className={styles.cardDescription}>
              Cadastre novas marcas antes de cadastrar lojas. Utilize os atalhos de cada registro para editar,
              remover ou incluir unidades rapidamente.
            </p>

            {isLoading ? <TableSkeleton columns={3} /> : null}
            {!isLoading && orderedBrands.length === 0 && !error ? (
              <div className={styles.emptyState}>Nenhuma marca cadastrada.</div>
            ) : null}

            <div className={styles.brandList}>
              {orderedBrands.map((brand) => {
                const brandStores = stores.filter((store) => store.marca_id === brand.id);
                const isExpanded = expandedBrands.has(brand.id);
                return (
                  <details
                    key={brand.id}
                    className={styles.brandItem}
                    open={isExpanded}
                    onToggle={(event) => toggleBrand(brand.id, event.currentTarget.open)}
                  >
                    <summary className={styles.brandSummary}>
                      <div className={styles.brandSummaryContent}>
                        <span className={styles.brandTitle}>{brand.marca}</span>
                        <p className={styles.brandMeta}>
                          Código Diságua: {brand.cod_disagua ?? "—"} · {brand.store_count} loja(s)
                        </p>
                      </div>
                      <div className={styles.brandActions}>
                        <Button size="sm" variant="secondary" type="button" onClick={() => startEditBrand(brand)}>
                          Editar
                        </Button>
                        <Button size="sm" variant="danger" type="button" onClick={() => handleDeleteBrand(brand)}>
                          Excluir
                        </Button>
                        <Button size="sm" type="button" onClick={() => handleAddStoreToBrand(brand.id)}>
                          + Loja
                        </Button>
                      </div>
                    </summary>

                    <div className={styles.storeContainer}>
                      {brandStores.length === 0 ? (
                        <p className={styles.emptyState}>Nenhuma loja cadastrada para esta marca.</p>
                      ) : (
                        <table className={styles.storeTable}>
                          <thead>
                            <tr>
                              <th>Loja</th>
                              <th>Código</th>
                              <th>Local entrega</th>
                              <th>Endereço</th>
                              <th>Município</th>
                              <th>UF</th>
                              <th>Valor 20L</th>
                              <th>Valor 10L</th>
                              <th>Valor 1500ml</th>
                              <th>Valor CX copo</th>
                              <th>Valor vasilhame</th>
                              <th>Ações</th>
                            </tr>
                          </thead>
                          <tbody>
                            {brandStores.map((store) => (
                              <tr key={store.id}>
                                <td>{store.loja}</td>
                                <td>{store.cod_disagua ?? "—"}</td>
                                <td>{store.local_entrega}</td>
                                <td>{store.endereco ?? "—"}</td>
                                <td>{store.municipio}</td>
                                <td>{store.uf}</td>
                                <td>{formatCurrency(store.valor_20l)}</td>
                                <td>{formatCurrency(store.valor_10l)}</td>
                                <td>{formatCurrency(store.valor_1500ml)}</td>
                                <td>{formatCurrency(store.valor_cx_copo)}</td>
                                <td>{formatCurrency(store.valor_vasilhame)}</td>
                                <td>
                                  <div className={styles.brandActions}>
                                    <Button
                                      size="sm"
                                      variant="secondary"
                                      type="button"
                                      onClick={() => startEditStore(store)}
                                    >
                                      Editar
                                    </Button>
                                    <Button
                                      size="sm"
                                      variant="danger"
                                      type="button"
                                      onClick={() => handleDeleteStore(store)}
                                    >
                                      Excluir
                                    </Button>
                                  </div>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      )}
                    </div>
                  </details>
                );
              })}
            </div>
          </Card>
        </section>

        <section
          id={storePanelId}
          role="tabpanel"
          aria-labelledby={storeTabId}
          hidden={activeTab !== "stores"}
          className={styles.tabPanel}
        >
          <Card
            title="Lojas cadastradas"
            subtitle="Gerencie pontos de venda vinculados às marcas."
            actions={
              <Button type="button" variant="secondary" onClick={handleOpenCreateStore}>
                Nova loja
              </Button>
            }
          >
            <p className={styles.cardDescription}>
              Acompanhe todas as lojas registradas e utilize os atalhos para editar ou remover unidades conforme
              necessário.
            </p>
            {isLoading ? <TableSkeleton columns={storeColumns.length} /> : null}
            {!isLoading && stores.length === 0 && !error ? (
              <div className={styles.emptyState}>Nenhuma loja cadastrada.</div>
            ) : null}
            {!isLoading && stores.length > 0 ? (
              <DataTable columns={storeColumns} data={stores} keyExtractor={(store) => store.id.toString()} />
            ) : null}
          </Card>
        </section>
      </div>

      <Modal
        isOpen={isBrandModalOpen}
        onClose={handleCloseBrandModal}
        title={brandMode === "create" ? "Cadastrar marca" : "Editar marca"}
        footer={
          <>
            <Button type="button" variant="ghost" onClick={handleCloseBrandModal}>
              Cancelar
            </Button>
            <Button
              type="submit"
              form="brand-form"
              isLoading={isSubmittingBrand}
              loadingText="Salvando..."
              disabled={!isBrandFormValid}
            >
              {brandMode === "create" ? "Cadastrar marca" : "Atualizar marca"}
            </Button>
          </>
        }
      >
        <form id="brand-form" className={styles.form} onSubmit={handleBrandSubmit}>
          <div className={styles.formSection}>
            <header className={styles.sectionHeader}>
              <h3>Dados da marca</h3>
              <p>Informe os campos obrigatórios antes de salvar.</p>
            </header>

            <div className={styles.formGrid}>
              <FormField label="Nome da marca" htmlFor="brand-name" error={brandErrors.marca}>
                <TextInput
                  id="brand-name"
                  value={brandForm.marca}
                  onChange={(event) => setBrandForm((current) => ({ ...current, marca: event.target.value }))}
                  hasError={Boolean(brandErrors.marca)}
                  required
                />
              </FormField>

              <FormField label="Código Diságua" htmlFor="brand-code">
                <TextInput
                  id="brand-code"
                  value={brandForm.cod_disagua ?? ""}
                  onChange={(event) => setBrandForm((current) => ({ ...current, cod_disagua: event.target.value }))}
                  placeholder="Opcional"
                />
              </FormField>
            </div>
          </div>
        </form>
      </Modal>

      <Modal
        isOpen={isStoreModalOpen}
        onClose={handleCloseStoreModal}
        title={storeMode === "create" ? "Cadastrar loja" : "Editar loja"}
        footer={
          <>
            <Button type="button" variant="ghost" onClick={handleCloseStoreModal}>
              Cancelar
            </Button>
            <Button
              type="submit"
              form="store-form"
              isLoading={isSubmittingStore}
              loadingText="Salvando..."
              disabled={!isStoreFormValid}
            >
              {storeMode === "create" ? "Cadastrar loja" : "Atualizar loja"}
            </Button>
          </>
        }
      >
        <form id="store-form" className={styles.form} onSubmit={handleStoreSubmit}>
          <div className={styles.formSection}>
            <header className={styles.sectionHeader}>
              <h3>Dados básicos</h3>
              <p>Defina a marca e as informações de localização da loja.</p>
            </header>

            <div className={styles.formGrid}>
              <FormField label="Marca" htmlFor="store-brand" error={storeErrors.marca_id}>
                <SelectInput
                  id="store-brand"
                  value={storeForm.marca_id}
                  onChange={(event) => setStoreForm((current) => ({ ...current, marca_id: event.target.value }))}
                  hasError={Boolean(storeErrors.marca_id)}
                  required
                >
                  <option value="" disabled>
                    Selecione
                  </option>
                  {orderedBrands.map((brand) => (
                    <option key={brand.id} value={brand.id}>
                      {brand.marca}
                    </option>
                  ))}
                </SelectInput>
              </FormField>

              <FormField label="Nome da loja" htmlFor="store-name" error={storeErrors.loja}>
                <TextInput
                  id="store-name"
                  value={storeForm.loja}
                  onChange={(event) => setStoreForm((current) => ({ ...current, loja: event.target.value }))}
                  hasError={Boolean(storeErrors.loja)}
                  required
                />
              </FormField>

              <FormField label="Código Diságua" htmlFor="store-code">
                <TextInput
                  id="store-code"
                  value={storeForm.cod_disagua}
                  onChange={(event) => setStoreForm((current) => ({ ...current, cod_disagua: event.target.value }))}
                  placeholder="Opcional"
                />
              </FormField>

              <FormField label="Local da entrega" htmlFor="store-delivery" error={storeErrors.local_entrega}>
                <TextInput
                  id="store-delivery"
                  value={storeForm.local_entrega}
                  onChange={(event) =>
                    setStoreForm((current) => ({ ...current, local_entrega: event.target.value }))
                  }
                  hasError={Boolean(storeErrors.local_entrega)}
                  required
                />
              </FormField>

              <FormField label="Endereço" htmlFor="store-address">
                <TextInput
                  id="store-address"
                  value={storeForm.endereco}
                  onChange={(event) => setStoreForm((current) => ({ ...current, endereco: event.target.value }))}
                  placeholder="Opcional"
                />
              </FormField>

              <FormField label="Município" htmlFor="store-city" error={storeErrors.municipio}>
                <TextInput
                  id="store-city"
                  value={storeForm.municipio}
                  onChange={(event) => setStoreForm((current) => ({ ...current, municipio: event.target.value }))}
                  hasError={Boolean(storeErrors.municipio)}
                  required
                />
              </FormField>

              <FormField label="UF" htmlFor="store-state" error={storeErrors.uf}>
                <SelectInput
                  id="store-state"
                  value={storeForm.uf}
                  onChange={(event) => setStoreForm((current) => ({ ...current, uf: event.target.value }))}
                  hasError={Boolean(storeErrors.uf)}
                  required
                >
                  <option value="" disabled>
                    Selecione
                  </option>
                  {BRAZIL_STATES.map((state) => (
                    <option key={state.value} value={state.value}>
                      {state.label}
                    </option>
                  ))}
                </SelectInput>
              </FormField>
            </div>
          </div>

          <div className={styles.formSection}>
            <header className={styles.sectionHeader}>
              <h3>Valores praticados</h3>
              <p>Ajuste os preços aplicados para cada item do mix.</p>
            </header>

            <div className={styles.tableWrapper}>
              <table className={styles.priceTable}>
                <thead>
                  <tr>
                    <th scope="col">Produto</th>
                    <th scope="col">Valor (R$)</th>
                  </tr>
                </thead>
                <tbody>
                  {STORE_PRICE_FIELDS.map((field) => {
                    const inputId = `store-price-${field.key}`;
                    return (
                      <tr key={field.key}>
                        <th scope="row">
                          {field.label}
                        </th>
                        <td>
                          <TextInput
                            id={inputId}
                            value={storeForm[field.key]}
                            onChange={(event) => handlePriceChange(field.key, event.target.value)}
                            inputMode="decimal"
                            placeholder="0,00"
                          />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </form>
      </Modal>

      <StoresImportModal
        isOpen={isImportModalOpen}
        onClose={handleCloseImport}
        onCompleted={handleImportCompleted}
      />
    </>
  );
}
