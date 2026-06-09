export function formatDate(iso) {
  if (!iso) return '—'
  return new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  }).format(new Date(iso))
}

export function formatDateOnly(iso) {
  if (!iso) return '—'
  return new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit', month: '2-digit', year: 'numeric'
  }).format(new Date(iso))
}

export function formatAmount(value, currency = 'XOF') {
  if (value == null) return '—'
  const num = new Intl.NumberFormat('fr-FR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
  return `${num} ${currency}`
}

export function formatPercent(value) {
  if (value == null) return '—'
  return `${Number(value).toFixed(1)} %`
}
