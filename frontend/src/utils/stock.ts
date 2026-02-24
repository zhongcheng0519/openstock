export const getStockColor = (val: number | null): string => {
  if (val === null || val === undefined) return 'color-neutral'
  if (val > 0) return 'color-up'
  if (val < 0) return 'color-down'
  return 'color-neutral'
}

export const formatStockNumber = (val: number | null, decimals: number = 2): string => {
  if (val === null || val === undefined) return '-'
  return val.toFixed(decimals)
}

export const formatStockPct = (val: number | null): string => {
  if (val === null || val === undefined) return '-'
  const prefix = val > 0 ? '+' : ''
  return `${prefix}${val.toFixed(2)}%`
}

export const formatStockMV = (val: number | null): string => {
  if (val === null || val === undefined) return '-'
  return (val / 10000).toFixed(2)
}

export const formatStockVol = (val: number | null): string => {
  if (val === null || val === undefined) return '-'
  return val.toFixed(0)
}

export const formatStockAmount = (val: number | null): string => {
  if (val === null || val === undefined) return '-'
  const prefix = val > 0 ? '+' : ''
  return `${prefix}${val.toFixed(2)}`
}
