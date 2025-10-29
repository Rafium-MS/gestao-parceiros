import { ChangeEvent, FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { FormField } from "@/components/ui/FormField";
import { SelectInput } from "@/components/ui/SelectInput";
import { TextInput } from "@/components/ui/TextInput";

import styles from "./ReportFilters.module.css";

export type ReportFiltersValue = {
  period: "7d" | "30d" | "90d" | "custom";
  status: "todos" | "ativos" | "pendentes" | "suspensos";
  channel: "todos" | "varejo" | "marketplace" | "food_service";
  partner: string;
  referenceMonth: string;
};

type ReportFiltersProps = {
  value: ReportFiltersValue;
  onChange: (value: ReportFiltersValue) => void;
  onApply: (value: ReportFiltersValue) => void;
  onReset?: () => void;
};

export function ReportFilters({ value, onChange, onApply, onReset }: ReportFiltersProps) {
  const handleFieldChange = (field: keyof ReportFiltersValue) =>
    (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      onChange({ ...value, [field]: event.target.value });
    };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onApply(value);
  };

  return (
    <Card
      title="Filtros avançados"
      subtitle="Refine as métricas selecionando período, status e canal de vendas."
    >
      <form className={styles.form} onSubmit={handleSubmit}>
        <div className={styles.row}>
          <FormField label="Período" htmlFor="filter-period">
            <SelectInput
              id="filter-period"
              value={value.period}
              onChange={handleFieldChange("period")}
            >
              <option value="7d">Últimos 7 dias</option>
              <option value="30d">Últimos 30 dias</option>
              <option value="90d">Últimos 90 dias</option>
              <option value="custom">Personalizado</option>
            </SelectInput>
          </FormField>

          <FormField label="Status do parceiro" htmlFor="filter-status">
            <SelectInput
              id="filter-status"
              value={value.status}
              onChange={handleFieldChange("status")}
            >
              <option value="todos">Todos</option>
              <option value="ativos">Ativos</option>
              <option value="pendentes">Pendentes</option>
              <option value="suspensos">Suspensos</option>
            </SelectInput>
          </FormField>

          <FormField label="Canal" htmlFor="filter-channel">
            <SelectInput
              id="filter-channel"
              value={value.channel}
              onChange={handleFieldChange("channel")}
            >
              <option value="todos">Todos</option>
              <option value="varejo">Varejo físico</option>
              <option value="marketplace">Marketplace</option>
              <option value="food_service">Food service</option>
            </SelectInput>
          </FormField>
        </div>

        <div className={styles.row}>
          <FormField
            label="Parceiro"
            htmlFor="filter-partner"
            helperText="Busque por nome fantasia para comparar indicadores."
            optional
          >
            <TextInput
              id="filter-partner"
              placeholder="Ex.: Rio Água"
              value={value.partner}
              onChange={handleFieldChange("partner")}
            />
          </FormField>

          <FormField label="Competência" htmlFor="filter-month" optional>
            <TextInput
              id="filter-month"
              type="month"
              value={value.referenceMonth}
              onChange={handleFieldChange("referenceMonth")}
            />
          </FormField>
        </div>

        <div className={styles.actions}>
          {onReset ? (
            <Button type="button" variant="ghost" onClick={onReset}>
              Limpar filtros
            </Button>
          ) : null}
          <Button type="submit">Aplicar filtros</Button>
        </div>
      </form>
    </Card>
  );
}
