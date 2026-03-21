export function isDemoMode(): boolean {
  return (
    import.meta.env.VITE_DEMO_MODE === 'true' ||
    import.meta.env.VITE_DEMO_MODE === '1'
  );
}
