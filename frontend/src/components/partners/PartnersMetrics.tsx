import { useMemo } from "react";

import { PartnerRecord } from "@/services/partners";

import styles from "./PartnersTable.module.css";

type PartnersMetricsProps = {
  partners: PartnerRecord[];
};

const numberFormatter = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
});

export function PartnersMetrics({ partners }: PartnersMetricsProps) {
  const metrics = useMemo(() => {
    if (partners.length === 0) {
      return [
        {
          label: "Parceiros cadastrados",
          value: "0",
          delta: "Cadastre novos parceiros para começar",
        },
      ];
    }

    const totalPartners = partners.length;
    const statesCovered = new Set(partners.map((partner) => partner.estado).filter(Boolean)).size;
    const contactsWithEmail = partners.filter((partner) => Boolean(partner.email)).length;
    const totalVolume = partners.reduce((total, partner) => total + partner.total, 0);
    const citiesCovered = new Set(partners.map((partner) => partner.cidade).filter(Boolean)).size;

    return [
      {
        label: "Parceiros cadastrados",
        value: totalPartners.toString(),
        delta: `${citiesCovered} cidades atendidas`,
      },
      {
        label: "Cobertura geográfica",
        value: `${statesCovered} UF${statesCovered === 1 ? "" : "s"}`,
        delta: "Expanda para novas regiões",
      },
      {
        label: "Contatos com e-mail",
        value: contactsWithEmail.toString(),
        delta:
          totalPartners > 0
            ? `${Math.round((contactsWithEmail / totalPartners) * 100)}% da base com contato digital`
            : "Atualize os cadastros",
      },
      {
        label: "Volume contratado",
        value: numberFormatter.format(totalVolume),
        delta: "Soma das categorias cadastradas",
      },
    ];
  }, [partners]);

  return (
    <div className={styles.metrics}>
      {metrics.map((metric) => (
        <div key={metric.label} className={styles.metricCard}>
          <span className={styles.metricLabel}>{metric.label}</span>
          <strong className={styles.metricValue}>{metric.value}</strong>
          <span className={styles.metricDelta}>{metric.delta}</span>
        </div>
      ))}
    </div>
  );
}
