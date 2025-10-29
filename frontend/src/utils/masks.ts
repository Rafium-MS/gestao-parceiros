export function formatCpfCnpj(value: string) {
  const digits = value.replace(/\D/g, "");

  if (digits.length <= 11) {
    const limited = digits.slice(0, 11);
    const part1 = limited.slice(0, 3);
    const part2 = limited.slice(3, 6);
    const part3 = limited.slice(6, 9);
    const part4 = limited.slice(9, 11);

    let formatted = part1;
    if (part2) {
      formatted += `.${part2}`;
    }
    if (part3) {
      formatted += `.${part3}`;
    }
    if (part4) {
      formatted += `-${part4}`;
    }
    return formatted ?? "";
  }

  const limited = digits.slice(0, 14);
  const part1 = limited.slice(0, 2);
  const part2 = limited.slice(2, 5);
  const part3 = limited.slice(5, 8);
  const part4 = limited.slice(8, 12);
  const part5 = limited.slice(12, 14);

  let formatted = part1;
  if (part2) {
    formatted += `.${part2}`;
  }
  if (part3) {
    formatted += `.${part3}`;
  }
  if (part4) {
    formatted += `/${part4}`;
  }
  if (part5) {
    formatted += `-${part5}`;
  }

  return formatted ?? "";
}

export function formatPhone(value: string) {
  const digits = value.replace(/\D/g, "").slice(0, 11);

  const part1 = digits.slice(0, 2);
  const part2 = digits.length > 10 ? digits.slice(2, 7) : digits.slice(2, 6);
  const part3 = digits.length > 10 ? digits.slice(7, 11) : digits.slice(6, 10);

  let formatted = "";
  if (part1) {
    formatted = `(${part1}`;
    if (part1.length === 2) {
      formatted += ") ";
    }
  }

  if (part2) {
    formatted += part2;
  }

  if (part3) {
    formatted += `-${part3}`;
  }

  return formatted.trim();
}

export function formatCurrencyInput(value: string) {
  const digits = value.replace(/\D/g, "");
  if (!digits) {
    return "";
  }

  const numericValue = Number.parseInt(digits, 10) / 100;
  return numericValue.toLocaleString("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

export function formatCurrencyFromNumber(value: number | null | undefined) {
  if (value === null || value === undefined) {
    return "";
  }

  return value.toLocaleString("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}
