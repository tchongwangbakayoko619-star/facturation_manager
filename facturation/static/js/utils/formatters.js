const locale = "fr-FR";

export function formatCurrency(value, currency = "XAF") {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return "—";
  return new Intl.NumberFormat(locale, {
    style: "currency", currency, maximumFractionDigits: 0,
  }).format(amount);
}

export function formatNumber(value, maximumFractionDigits = 2) {
  const number = Number(value);
  return Number.isFinite(number)
    ? new Intl.NumberFormat(locale, { maximumFractionDigits }).format(number)
    : "—";
}

export function formatDate(value, options = { dateStyle: "medium" }) {
  if (!value) return "—";
  const date = new Date(`${value}T00:00:00`);
  return Number.isNaN(date.getTime()) ? "—" : new Intl.DateTimeFormat(locale, options).format(date);
}
