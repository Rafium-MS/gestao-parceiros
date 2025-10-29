import { useEffect, useMemo, useState } from "react";

import { Card } from "@/components/ui/Card";
import { DataTable, TableColumn } from "@/components/ui/DataTable";
import { listBrands, type BrandRecord } from "@/services/brands";
import { listStores, type StoreRecord } from "@/services/stores";
import { formatCurrency } from "@/utils/formatters";

import styles from "./StoresPage.module.css";

type SummaryMetric = {
  label: string;
  value: string;
  helper?: string;
};

export function StoresPage() {
  const [brands, setBrands] = useState<BrandRecord[]>([]);
  const [stores, setStores] = useState<StoreRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setIsLoading(true);
    setError(null);

    Promise.all([listBrands(), listStores()])
      .then(([brandList, storeList]) => {
        if (active) {
          setBrands(brandList);
          setStores(storeList);
        }
      })
      .catch((err: unknown) => {
        if (active) {
          const message = err instanceof Error ? err.message : "Não foi possível carregar marcas e lojas.";
          setError(message);
          setBrands([]);
          setStores([]);
        }
      })
      .finally(() => {
        if (active) {
          setIsLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

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

  const brandColumns = useMemo<TableColumn<BrandRecord>[]>(
    () => [
      { header: "Marca", accessor: "marca" },
      {
        header: "Código Diságua",
        render: (brand) => brand.cod_disagua ?? "—",
      },
      {
        header: "Lojas vinculadas",
        align: "right",
        render: (brand) => brand.store_count.toString(),
      },
    ],
    [],
  );

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

      <div className={styles.grid}>
        <Card title="Marcas cadastradas" subtitle="Informações sincronizadas com o banco de dados.">
          {error ? <div className={styles.errorMessage}>{error}</div> : null}
          {isLoading ? <div className={styles.loadingMessage}>Carregando marcas...</div> : null}
          {!isLoading && brands.length === 0 && !error ? (
            <div className={styles.emptyState}>Nenhuma marca cadastrada.</div>
          ) : null}
          {!isLoading && brands.length > 0 ? (
            <DataTable columns={brandColumns} data={brands} keyExtractor={(brand) => brand.id.toString()} />
          ) : null}
        </Card>

        <Card title="Lojas cadastradas" subtitle="Listagem das unidades comerciais ativas.">
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
    </div>
  );
}
