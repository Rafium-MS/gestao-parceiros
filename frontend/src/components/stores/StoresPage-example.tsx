// Este é um exemplo de como refatorar a StoresPage para usar os novos modais
// Coloque este arquivo em: frontend/src/pages/StoresPage.tsx

import { useCallback, useEffect, useMemo, useState } from "react";

import { BrandModal } from "@/components/brands/BrandModal";
import { StoreModal } from "@/components/stores/StoreModal";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useConfirmDialog } from "@/components/ui/ConfirmDialog/useConfirmDialog";
import { useToast } from "@/components/ui/Toast/useToast";
import { deleteBrand, deleteStore, listBrands, listStores } from "@/services/api";
import { BrandRecord, StoreRecord } from "@/types";
import { formatCurrency } from "@/utils/currency";

import styles from "./StoresPage.module.css";

export function StoresPage() {
  const [brands, setBrands] = useState<BrandRecord[]>([]);
  const [stores, setStores] = useState<StoreRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Estados do modal de marca
  const [isBrandModalOpen, setIsBrandModalOpen] = useState(false);
  const [editingBrand, setEditingBrand] = useState<BrandRecord | null>(null);
  
  // Estados do modal de loja
  const [isStoreModalOpen, setIsStoreModalOpen] = useState(false);
  const [editingStore, setEditingStore] = useState<StoreRecord | null>(null);
  const [preselectedBrandId, setPreselectedBrandId] = useState<number | undefined>(undefined);
  
  const [expandedBrands, setExpandedBrands] = useState<Set<number>>(new Set());
  
  const { showSuccess, showError } = useToast();
  const { confirm: requestConfirmation, dialog: confirmDialog } = useConfirmDialog();

  const loadAll = useCallback(() => {
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
        showError(message);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [showError]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  const metrics = useMemo(() => {
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

  // Handlers do modal de marca
  const handleOpenBrandModal = () => {
    setEditingBrand(null);
    setIsBrandModalOpen(true);
  };

  const handleEditBrand = (brand: BrandRecord) => {
    setEditingBrand(brand);
    setIsBrandModalOpen(true);
  };

  const handleBrandSuccess = () => {
    showSuccess(editingBrand ? "Marca atualizada com sucesso." : "Marca cadastrada com sucesso.");
    loadAll();
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

  // Handlers do modal de loja
  const handleOpenStoreModal = (brandId?: number) => {
    setEditingStore(null);
    setPreselectedBrandId(brandId);
    setIsStoreModalOpen(true);
  };

  const handleEditStore = (store: StoreRecord) => {
    setEditingStore(store);
    setPreselectedBrandId(undefined);
    setIsStoreModalOpen(true);
  };

  const handleStoreSuccess = () => {
    showSuccess(editingStore ? "Loja atualizada com sucesso." : "Loja cadastrada com sucesso.");
    loadAll();
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
    <>
      {confirmDialog}
      <BrandModal
        isOpen={isBrandModalOpen}
        onClose={() => setIsBrandModalOpen(false)}
        onSuccess={handleBrandSuccess}
        editingBrand={editingBrand}
      />
      <StoreModal
        isOpen={isStoreModalOpen}
        onClose={() => setIsStoreModalOpen(false)}
        onSuccess={handleStoreSuccess}
        editingStore={editingStore}
        brands={brands}
        preselectedBrandId={preselectedBrandId}
      />

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

        <div className={styles.actions}>
          <Button onClick={handleOpenBrandModal}>
            Adicionar marca
          </Button>
          <Button onClick={() => handleOpenStoreModal()}>
            Adicionar loja
          </Button>
        </div>

        {error ? <div className={styles.errorMessage}>{error}</div> : null}
        {isLoading ? <div className={styles.loadingMessage}>Carregando...</div> : null}

        {!isLoading && orderedBrands.length === 0 && !error ? (
          <div className={styles.emptyState}>Nenhuma marca cadastrada ainda.</div>
        ) : null}

        {!isLoading && orderedBrands.length > 0 ? (
          <Card>
            <div className={styles.brandsList}>
              {orderedBrands.map((brand) => {
                const brandStores = stores.filter((store) => store.marca_id === brand.id);
                const isExpanded = expandedBrands.has(brand.id);

                return (
                  <details
                    key={brand.id}
                    className={styles.brandItem}
                    open={isExpanded}
                    onToggle={(event) => {
                      toggleBrand(brand.id, event.currentTarget.open);
                    }}
                  >
                    <summary className={styles.brandHeader}>
                      <div className={styles.brandInfo}>
                        <h3 className={styles.brandName}>{brand.marca}</h3>
                        <p className={styles.brandMeta}>
                          {brand.cod_disagua ?? "—"} · {brand.store_count} loja(s)
                        </p>
                      </div>
                      <div className={styles.brandActions}>
                        <Button size="sm" variant="secondary" type="button" onClick={() => handleEditBrand(brand)}>
                          Editar
                        </Button>
                        <Button size="sm" variant="danger" type="button" onClick={() => handleDeleteBrand(brand)}>
                          Excluir
                        </Button>
                        <Button size="sm" type="button" onClick={() => handleOpenStoreModal(brand.id)}>
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
                              <th>Município</th>
                              <th>UF</th>
                              <th>Mix total</th>
                              <th>Ações</th>
                            </tr>
                          </thead>
                          <tbody>
                            {brandStores.map((store) => (
                              <tr key={store.id}>
                                <td>{store.loja}</td>
                                <td>{store.cod_disagua ?? "—"}</td>
                                <td>{store.local_entrega}</td>
                                <td>{store.municipio}</td>
                                <td>{store.uf}</td>
                                <td>
                                  {formatCurrency(
                                    store.valor_20l +
                                      store.valor_10l +
                                      store.valor_1500ml +
                                      store.valor_cx_copo +
                                      store.valor_vasilhame,
                                  )}
                                </td>
                                <td>
                                  <div className={styles.storeActions}>
                                    <Button
                                      size="sm"
                                      variant="secondary"
                                      type="button"
                                      onClick={() => handleEditStore(store)}
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
        ) : null}
      </div>
    </>
  );
}
