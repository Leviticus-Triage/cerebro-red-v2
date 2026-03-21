/** Minimal toast (replace with Sonner/shadcn if desired). */
export const toast = {
  success: (msg: string) => {
    if (typeof window !== 'undefined') {
      console.info('[toast]', msg);
    }
  },
  error: (msg: string) => {
    if (typeof window !== 'undefined') {
      console.error('[toast]', msg);
    }
  },
  info: (msg: string) => {
    if (typeof window !== 'undefined') {
      console.info('[toast]', msg);
    }
  },
  warning: (msg: string) => {
    if (typeof window !== 'undefined') {
      console.warn('[toast]', msg);
    }
  },
};
