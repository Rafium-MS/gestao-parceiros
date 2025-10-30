import { useCallback, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { DataTable, TableColumn } from "@/components/ui/DataTable";
import { TableSkeleton } from "@/components/ui/TableSkeleton";
import { useConfirmDialog } from "@/hooks/useConfirmDialog";
import { useDisclosure } from "@/hooks/useDisclosure";
import { PartnerForm, PartnerFormMode } from "@/components/partners/PartnerForm";
import { PartnersMetrics } from "@/components/partners/PartnersMetrics";
import { usePartnersData } from "@/components/partners/hooks/usePartnersData";
import { PartnerPayload, PartnerRecord } from "@/services/partners";
import { formatDate } from "@/utils/formatters";

import styles from "./PartnersTable.module.css";

const numberFormatter = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
});

export function PartnersTable() {
  const { isOpen, open, close } = useDisclosure();
  const { confirm: requestConfirmation, dialog: confirmDialog } = useConfirmDialog();
  const [mode, setMode] = useState<PartnerFormMode>("create");
  const [editingPartner, setEditingPartner] = useState<PartnerRecord | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const {
    partners,
    partnersQuery,
    createPartner,
    updatePartner,
    deletePartner,
    deleteManyPartners,
    isCreatingPartner,
    isUpdatingPartner,
    isBulkDeletingPartners,
  } = usePartnersData();

  const isLoading = partnersQuery.isPending;
  const fetchError = partnersQuery.error
    ? partnersQuery.error instanceof Error
      ? partnersQuery.error.message
      : "Não foi possível carregar os parceiros."
    : null;

  const handleOpenCreate = () => {
    setMode("create");
    setEditingPartner(null);
    setActionError(null);
    open();
  };

  const handleCloseForm = useCallback(() => {
    close();
    setEditingPartner(null);
  }, [close]);

  const handleEdit = useCallback(
    (partner: PartnerRecord) => {
      setMode("edit");
      setEditingPartner(partner);
      setActionError(null);
      open();
    },
    [open],
  );

  const handleDelete = useCallback(
    async (partner: PartnerRecord) => {
      const confirmed = await requestConfirmation({
        title: "Remover parceiro",
        description: `Tem certeza de que deseja excluir o parceiro ${partner.parceiro}? Essa ação não poderá ser desfeita.`,
        confirmLabel: "Excluir parceiro",
        confirmVariant: "danger",
        tone: "danger",
      });

      if (!confirmed) {
        return;
      }

      setActionError(null);
      try {
        await deletePartner(partner.id);
      } catch (error) {
        const message =
          error instanceof Error ? error.message : "Não foi possível excluir o parceiro.";
        setActionError(message);
      }
    },
    [deletePartner, requestConfirmation],
  );

  const handleBulkDelete = useCallback(
    async (selected: PartnerRecord[], clearSelection: () => void) => {
      if (selected.length === 0) {
        return;
      }

      const confirmed = await requestConfirmation({
        title: selected.length === 1 ? "Remover parceiro" : "Remover parceiros",
        description:
          selected.length === 1
            ? `Tem certeza de que deseja excluir o parceiro ${selected[0].parceiro}? Essa ação não poderá ser desfeita.`
            : `Tem certeza de que deseja excluir ${selected.length} parceiros selecionados? Essa ação não poderá ser desfeita.`,
        confirmLabel: selected.length === 1 ? "Excluir parceiro" : "Excluir parceiros",
        confirmVariant: "danger",
        tone: "danger",
      });

      if (!confirmed) {
        return;
      }

      setActionError(null);
      try {
        await deleteManyPartners(selected.map((partner) => partner.id));
        clearSelection();
      } catch (error) {
        const message =
          error instanceof Error
            ? error.message
            : "Não foi possível excluir os parceiros selecionados.";
        setActionError(message);
      }
    },
    [deleteManyPartners, requestConfirmation],
  );

  const renderSelectionActions = useCallback(
    (selected: PartnerRecord[], clearSelection: () => void) => (
      <Button
        size="sm"
        variant="danger"
        onClick={() => handleBulkDelete(selected, clearSelection)}
        isLoading={isBulkDeletingPartners}
        loadingText="Excluindo..."
      >
        {`Excluir ${selected.length > 1 ? "selecionados" : "selecionado"}`}
      </Button>
    ),
    [handleBulkDelete, isBulkDeletingPartners],
  );

  const columns = useMemo<TableColumn<PartnerRecord>[]>(
    () => [
      { header: "Parceiro", accessor: "parceiro", sortable: true },
      { header: "Documento", accessor: "cnpj_cpf", sortable: true },
      {
        header: "Localização",
        render: (partner) => `${partner.cidade} - ${partner.estado}`,
        sortable: true,
        sortValue: (partner) => `${partner.cidade ?? ""} ${partner.estado ?? ""}`,
        exportValue: (partner) => `${partner.cidade ?? ""} - ${partner.estado ?? ""}`,
      },
      { header: "Telefone", accessor: "telefone", sortable: true },
      {
        header: "E-mail",
        render: (partner) => partner.email ?? "—",
        sortable: true,
        exportValue: (partner) => partner.email ?? "",
      },
      {
        header: "Volume total",
        align: "right",
        render: (partner) => numberFormatter.format(partner.total),
        sortable: true,
        sortValue: (partner) => partner.total,
        exportValue: (partner) => partner.total,
      },
      {
        header: "Cadastro",
        render: (partner) => (partner.created_at ? formatDate(partner.created_at) : "—"),
        sortable: true,
        sortValue: (partner) => (partner.created_at ? new Date(partner.created_at) : null),
        exportValue: (partner) => partner.created_at ?? "",
      },
      {
        header: "Ações",
        width: "160px",
        disableExport: true,
        render: (partner) => (
          <div className={styles.tableActions}>
            <Button size="sm" variant="secondary" onClick={() => handleEdit(partner)}>
              Editar
            </Button>
            <Button size="sm" variant="danger" onClick={() => handleDelete(partner)}>
              Excluir
            </Button>
          </div>
        ),
      },
    ],
    [handleDelete, handleEdit],
  );

  const handleFormSubmit = useCallback(
    async (payload: PartnerPayload) => {
      if (mode === "create") {
        await createPartner(payload);
        return;
      }

      if (editingPartner) {
        await updatePartner({ id: editingPartner.id, payload });
        return;
      }

      throw new Error("Nenhum parceiro selecionado para edição.");
    },
    [createPartner, editingPartner, mode, updatePartner],
  );

  const isSubmittingForm = mode === "create" ? isCreatingPartner : isUpdatingPartner;

  return (
    <>
      {confirmDialog}
      <Card
        title="Parceiros cadastrados"
        subtitle="Acompanhe e cadastre os parceiros que fazem parte da rede de distribuição."
        actions={
          <Button onClick={handleOpenCreate} data-testid="open-partner-modal">
            Adicionar parceiro
          </Button>
        }
      >
        <PartnersMetrics partners={partners} />

        {fetchError ? <div className={styles.errorMessage}>{fetchError}</div> : null}
        {actionError ? <div className={styles.errorMessage}>{actionError}</div> : null}

        {isLoading ? <TableSkeleton columns={columns.length} /> : null}

        {!isLoading && partners.length === 0 && !fetchError ? (
          <div className={styles.feedback}>Nenhum parceiro cadastrado até o momento.</div>
        ) : null}

        {!isLoading && partners.length > 0 ? (
          <DataTable
            columns={columns}
            data={partners}
            keyExtractor={(partner) => partner.id.toString()}
            enableSorting
            initialSort={{ columnKey: "parceiro", direction: "asc" }}
            enablePagination
            enableSelection
            selectionActions={renderSelectionActions}
            enableExport
            exportFileName="parceiros"
          />
        ) : null}

        <PartnerForm
          isOpen={isOpen}
          mode={mode}
          onClose={handleCloseForm}
          onSubmit={handleFormSubmit}
          partner={editingPartner}
          partners={partners}
          isSubmitting={isSubmittingForm}
        />
      </Card>
    </>
  );
}
