import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export function formatDate(s: string | Date | undefined): string {
  if (!s) return '—';
  try {
    const d = typeof s === 'string' ? new Date(s) : s;
    return d.toLocaleString();
  } catch {
    return String(s);
  }
}

export function getSeverityBadgeVariant(
  severity: string
): 'default' | 'destructive' | 'secondary' | 'outline' {
  const sev = severity?.toLowerCase();
  if (sev === 'critical' || sev === 'high') return 'destructive';
  if (sev === 'medium') return 'default';
  return 'secondary';
}
