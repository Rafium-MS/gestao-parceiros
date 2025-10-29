import { FormEvent, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable, TableColumn } from "@/components/ui/DataTable";
import { FormField } from "@/components/ui/FormField";
import { SelectInput } from "@/components/ui/SelectInput";
import { TextInput } from "@/components/ui/TextInput";
import {
  createBrand,
  deleteBrand,
  listBrands,
  type BrandPayload,
  type BrandRecord,
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

import styles from "./StoresPage.module.css";

type SummaryMetric = {
  label: string;
  value: string;
  helper?: string;
};

type BrandFormErrors = {
  marca?: string;
  global?: string;
};

type StoreFormErrors = {
  marca_id?: string;
  loja?: string;
  local_entrega?: string;
  municipio?: string;
  uf?: string;
  global?: string;
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
  const [brandFeedback, setBrandFeedback] = useState<string | null>(null);
  const [isSubmittingBrand, setIsSubmittingBrand] = useState(false);
  const [storeForm, setStoreForm] = useState<StoreFormState>(defaultStoreForm);
  const [storeErrors, setStoreErrors] = useState<StoreFormErrors>({});
  const [storeMode, setStoreMode] = useState<FormMode>("create");
  const [editingStoreId, setEditingStoreId] = useState<number | null>(null);
  const [storeFeedback, setStoreFeedback] = useState<string | null>(null);
  const [isSubmittingStore, setIsSubmittingStore] = useState(false);
  const [expandedBrands, setExpandedBrands] = useState<Set<number>>(new Set());

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = () => {
    setIsLoading(true);
    setError(null);

    Promise.all([listBrands(), listStores()])
      .then(([brandList, storeList]) => {
        setBrands(brandList);
        setStores(storeList);
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : "Não foi possível carregar marcas e lojas.";
        setError(message);
        setBrands([]);
        setStores([]);
      })
      .finally(() => {
        setIsLoading(false);
      });
  };

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
        helper: topBrand ? `Maior portfólio: ${topBrand.marca}` : undefined,
      },
      {
        label: "Lojas cadastradas",
        value: totalStores.toString(),
        helper: totalBrands > 0 ? `${avgStoresPerBrand.toFixed(1)} lojas por marca` : undefined,
      },
      {
        label: "Investimento médio",
        value: totalStores > 0 ? formatCurrency(totalInvestimento / totalStores) : "R$ 0,00",
        helper: "Soma dos valores praticados por loja",
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

  const handleBrandSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setBrandErrors({});
    setBrandFeedback(null);

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
        setBrandFeedback("Marca cadastrada com sucesso.");
      } else if (editingBrandId !== null) {
        await updateBrand(editingBrandId, {
          marca: brandForm.marca.trim(),
          cod_disagua: brandForm.cod_disagua?.trim() || null,
        });
        setBrandFeedback("Marca atualizada com sucesso.");
      }
      setBrandForm({ marca: "", cod_disagua: "" });
      setBrandMode("create");
      setEditingBrandId(null);
      await loadAll();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível salvar a marca.";
      setBrandErrors({ global: message });
    } finally {
      setIsSubmittingBrand(false);
    }
  };

  const handleBrandReset = () => {
    setBrandForm({ marca: "", cod_disagua: "" });
    setBrandMode("create");
    setEditingBrandId(null);
    setBrandErrors({});
    setBrandFeedback(null);
  };

  const startEditBrand = (brand: BrandRecord) => {
    setBrandForm({ marca: brand.marca, cod_disagua: brand.cod_disagua ?? "" });
    setBrandMode("edit");
    setEditingBrandId(brand.id);
    setBrandErrors({});
    setBrandFeedback("Editando marca. Salve ou cancele para concluir.");
  };

  const handleDeleteBrand = async (brand: BrandRecord) => {
    if (!window.confirm(`Deseja excluir a marca ${brand.marca}?`)) {
      return;
    }
    try {
      await deleteBrand(brand.id);
      await loadAll();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível excluir a marca.";
      setBrandErrors({ global: message });
    }
  };

  const handleStoreSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setStoreErrors({});
    setStoreFeedback(null);

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
        setStoreFeedback("Loja cadastrada com sucesso.");
      } else if (editingStoreId !== null) {
        await updateStore(editingStoreId, payload);
        setStoreFeedback("Loja atualizada com sucesso.");
      }
      setStoreForm(defaultStoreForm);
      setStoreMode("create");
      setEditingStoreId(null);
      await loadAll();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível salvar a loja.";
      setStoreErrors({ global: message });
    } finally {
      setIsSubmittingStore(false);
    }
  };

  const handleStoreReset = () => {
    setStoreForm(defaultStoreForm);
    setStoreMode("create");
    setEditingStoreId(null);
    setStoreErrors({});
    setStoreFeedback(null);
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
    setStoreFeedback("Editando loja. Salve ou cancele para concluir.");
  };

  const handleDeleteStore = async (store: StoreRecord) => {
    if (!window.confirm(`Deseja excluir a loja ${store.loja}?`)) {
      return;
    }
    try {
      await deleteStore(store.id);
      await loadAll();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Não foi possível excluir a loja.";
      setStoreErrors({ global: message });
    }
  };

  const handleAddStoreToBrand = (brandId: number) => {
    setStoreForm((current) => ({ ...current, marca_id: String(brandId) }));
    setStoreMode("create");
    setEditingStoreId(null);
    setStoreErrors({});
    setStoreFeedback("Preencha os dados da nova loja.");
    document.getElementById("store-form")?.scrollIntoView({ behavior: "smooth" });
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

  return (
    <div className={styles.container}>
      <header className="page-header">
        <h1>Marcas e Lojas</h1>
        <p>Gerencie marcas, lojas e políticas comerciais com base nos dados registrados pelo backend.</p>
      </header>

      <section className={styles.summary} aria-live="polite">
        {metrics.map((metric) => (
          <div key={metric.label} className={styles.summaryCard}>
            <span className={styles.summaryLabel}>{metric.label}</span>
            <strong className={styles.summaryValue}>{metric.value}</strong>
            {metric.helper ? <span className={styles.summaryHelper}>{metric.helper}</span> : null}
          </div>
        ))}
      </section>

      <div className={styles.managementGrid}>
        <Card title={brandMode === "create" ? "Cadastro de marcas" : "Editar marca"}>
          <form className={styles.form} onSubmit={handleBrandSubmit} onReset={handleBrandReset}>
            {brandErrors.global ? <div className={styles.errorMessage}>{brandErrors.global}</div> : null}
            {brandFeedback ? (
              <div className={styles.successMessage} role="status" aria-live="polite">
                {brandFeedback}
              </div>
            ) : null}

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

            <div className={styles.formActions}>
              <Button type="submit" disabled={isSubmittingBrand}>
                {isSubmittingBrand ? "Salvando..." : brandMode === "create" ? "Cadastrar marca" : "Atualizar marca"}
              </Button>
              <Button type="reset" variant="ghost">
                Limpar
              </Button>
            </div>
          </form>
        </Card>

        <Card title={storeMode === "create" ? "Cadastro de lojas" : "Editar loja"}>
          <form
            id="store-form"
            className={styles.form}
            onSubmit={handleStoreSubmit}
            onReset={handleStoreReset}
          >
            {storeErrors.global ? <div className={styles.errorMessage}>{storeErrors.global}</div> : null}
            {storeFeedback ? (
              <div className={styles.successMessage} role="status" aria-live="polite">
                {storeFeedback}
              </div>
            ) : null}

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
                onChange={(event) => setStoreForm((current) => ({ ...current, local_entrega: event.target.value }))}
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

            <div className={styles.formRow}>
              <FormField label="Município" htmlFor="store-city" error={storeErrors.municipio}>
                <TextInput
                  id="store-city"
                  value={storeForm.municipio}
                  onChange={(event) => setStoreForm((current) => ({ ...current, municipio: event.target.value }))}
                  hasError={Boolean(storeErrors.municipio)}
                  required
                />
              </FormField>

              <FormField label="UF" htmlFor="store-uf" error={storeErrors.uf}>
                <SelectInput
                  id="store-uf"
                  value={storeForm.uf}
                  onChange={(event) => setStoreForm((current) => ({ ...current, uf: event.target.value }))}
                  hasError={Boolean(storeErrors.uf)}
                  required
                >
                  <option value="" disabled>
                    Selecione
                  </option>
                  {BRAZIL_STATES.map((uf) => (
                    <option key={uf.value} value={uf.value}>
                      {uf.label}
                    </option>
                  ))}
                </SelectInput>
              </FormField>
            </div>

            <div className={styles.formRow}>
              <FormField label="Valor 20 litros" htmlFor="store-valor-20">
                <TextInput
                  id="store-valor-20"
                  type="number"
                  min={0}
                  step="0.01"
                  value={storeForm.valor_20l}
                  onChange={(event) => setStoreForm((current) => ({ ...current, valor_20l: event.target.value }))}
                />
              </FormField>
              <FormField label="Valor 10 litros" htmlFor="store-valor-10">
                <TextInput
                  id="store-valor-10"
                  type="number"
                  min={0}
                  step="0.01"
                  value={storeForm.valor_10l}
                  onChange={(event) => setStoreForm((current) => ({ ...current, valor_10l: event.target.value }))}
                />
              </FormField>
              <FormField label="Valor 1500 ml" htmlFor="store-valor-1500">
                <TextInput
                  id="store-valor-1500"
                  type="number"
                  min={0}
                  step="0.01"
                  value={storeForm.valor_1500ml}
                  onChange={(event) => setStoreForm((current) => ({ ...current, valor_1500ml: event.target.value }))}
                />
              </FormField>
            </div>

            <div className={styles.formRow}>
              <FormField label="Valor CX copo" htmlFor="store-valor-copo">
                <TextInput
                  id="store-valor-copo"
                  type="number"
                  min={0}
                  step="0.01"
                  value={storeForm.valor_cx_copo}
                  onChange={(event) => setStoreForm((current) => ({ ...current, valor_cx_copo: event.target.value }))}
                />
              </FormField>
              <FormField label="Valor vasilhame" htmlFor="store-valor-vasilhame">
                <TextInput
                  id="store-valor-vasilhame"
                  type="number"
                  min={0}
                  step="0.01"
                  value={storeForm.valor_vasilhame}
                  onChange={(event) => setStoreForm((current) => ({ ...current, valor_vasilhame: event.target.value }))}
                />
              </FormField>
            </div>

            <div className={styles.formActions}>
              <Button type="submit" disabled={isSubmittingStore}>
                {isSubmittingStore ? "Salvando..." : storeMode === "create" ? "Cadastrar loja" : "Atualizar loja"}
              </Button>
              <Button type="reset" variant="ghost">
                Limpar
              </Button>
            </div>
          </form>
        </Card>
      </div>

      <Card title="Marcas cadastradas" subtitle="Informações sincronizadas com o banco de dados.">
        {error ? <div className={styles.errorMessage}>{error}</div> : null}
        {isLoading ? <div className={styles.loadingMessage}>Carregando marcas...</div> : null}
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
                open={isExpanded}
                onToggle={(event) => toggleBrand(brand.id, event.currentTarget.open)}
              >
                <summary className={styles.brandSummary}>
                  <div>
                    <h3>{brand.marca}</h3>
                    <p>
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
                                <Button size="sm" variant="secondary" type="button" onClick={() => startEditStore(store)}>
                                  Editar
                                </Button>
                                <Button size="sm" variant="danger" type="button" onClick={() => handleDeleteStore(store)}>
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

      <Card title="Lojas cadastradas" subtitle="Listagem consolidada das unidades comerciais ativas.">
        {error ? <div className={styles.errorMessage}>{error}</div> : null}
        {isLoading ? <div className={styles.loadingMessage}>Carregando lojas...</div> : null}
        {!isLoading && stores.length === 0 && !error ? (
          <div className={styles.emptyState}>Nenhuma loja cadastrada.</div>
        ) : null}
        {!isLoading && stores.length > 0 ? (
          <DataTable columns={storeColumns} data={stores} keyExtractor={(store) => store.id.toString()} />
        ) : null}
      </Card>
    </div>
  );
}
