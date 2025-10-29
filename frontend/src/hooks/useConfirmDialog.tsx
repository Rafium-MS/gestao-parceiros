import { useCallback, useMemo, useRef, useState } from "react";

import { ConfirmDialog, ConfirmDialogProps } from "@/components/ui/ConfirmDialog";

type ConfirmDialogOptions = Omit<ConfirmDialogProps, "isOpen" | "onConfirm" | "onCancel">;

type UseConfirmDialogReturn = {
  confirm: (options: ConfirmDialogOptions) => Promise<boolean>;
  dialog: JSX.Element | null;
};

export function useConfirmDialog(): UseConfirmDialogReturn {
  const [isOpen, setIsOpen] = useState(false);
  const [options, setOptions] = useState<ConfirmDialogOptions | null>(null);
  const resolverRef = useRef<(value: boolean) => void>();

  const handleClose = useCallback((result: boolean) => {
    setIsOpen(false);
    setOptions(null);
    if (resolverRef.current) {
      resolverRef.current(result);
      resolverRef.current = undefined;
    }
  }, []);

  const confirm = useCallback((dialogOptions: ConfirmDialogOptions) => {
    setOptions(dialogOptions);
    setIsOpen(true);
    return new Promise<boolean>((resolve) => {
      resolverRef.current = resolve;
    });
  }, []);

  const dialog = useMemo(() => {
    if (!options) {
      return null;
    }

    return (
      <ConfirmDialog
        isOpen={isOpen}
        onCancel={() => handleClose(false)}
        onConfirm={() => handleClose(true)}
        {...options}
      />
    );
  }, [handleClose, isOpen, options]);

  return { confirm, dialog };
}
