import { QueryKey, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createPartner,
  deletePartner,
  listPartners,
  PartnerPayload,
  PartnerRecord,
  updatePartner,
} from "@/services/partners";

const PARTNERS_QUERY_KEY: QueryKey = ["partners"];

type UpdatePartnerVariables = {
  id: number;
  payload: Partial<PartnerPayload>;
};

export function usePartnersData() {
  const queryClient = useQueryClient();

  const partnersQuery = useQuery<PartnerRecord[], Error>({
    queryKey: PARTNERS_QUERY_KEY,
    queryFn: listPartners,
    staleTime: 1000 * 60 * 5,
  });

  const createMutation = useMutation({
    mutationFn: createPartner,
    onSuccess: (createdPartner) => {
      queryClient.setQueryData<PartnerRecord[] | undefined>(
        PARTNERS_QUERY_KEY,
        (current) => (current ? [createdPartner, ...current] : [createdPartner]),
      );
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: UpdatePartnerVariables) => updatePartner(id, payload),
    onSuccess: (updatedPartner) => {
      queryClient.setQueryData<PartnerRecord[] | undefined>(
        PARTNERS_QUERY_KEY,
        (current) =>
          current?.map((partner) => (partner.id === updatedPartner.id ? updatedPartner : partner)) ?? [],
      );
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deletePartner(id),
    onSuccess: (_, id) => {
      queryClient.setQueryData<PartnerRecord[] | undefined>(
        PARTNERS_QUERY_KEY,
        (current) => current?.filter((partner) => partner.id !== id) ?? [],
      );
    },
  });

  const bulkDeleteMutation = useMutation({
    mutationFn: async (ids: number[]) => {
      await Promise.all(ids.map((id) => deletePartner(id)));
      return ids;
    },
    onSuccess: (ids) => {
      const idsToRemove = new Set(ids);
      queryClient.setQueryData<PartnerRecord[] | undefined>(
        PARTNERS_QUERY_KEY,
        (current) => current?.filter((partner) => !idsToRemove.has(partner.id)) ?? [],
      );
    },
  });

  const partners = partnersQuery.data ?? [];

  return {
    partners,
    partnersQuery,
    createPartner: createMutation.mutateAsync,
    updatePartner: updateMutation.mutateAsync,
    deletePartner: deleteMutation.mutateAsync,
    deleteManyPartners: bulkDeleteMutation.mutateAsync,
    isCreatingPartner: createMutation.isPending,
    isUpdatingPartner: updateMutation.isPending,
    isDeletingPartner: deleteMutation.isPending,
    isBulkDeletingPartners: bulkDeleteMutation.isPending,
  } as const;
}

export type UsePartnersDataReturn = ReturnType<typeof usePartnersData>;
