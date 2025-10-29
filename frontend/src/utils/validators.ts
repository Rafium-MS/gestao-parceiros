export function isRequired(value: string | null | undefined) {
  return !!value && value.trim().length > 0;
}

export function isEmail(value: string) {
  return /^[\w-.]+@([\w-]+\.)+[\w-]{2,}$/i.test(value);
}

export function minLength(value: string, length: number) {
  return value.trim().length >= length;
}

export function isCpfOrCnpj(value: string) {
  const digits = value.replace(/[^\d]/g, "");
  return digits.length === 11 || digits.length === 14;
}
