/**
 * Main App component with routing and providers.
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '@/lib/queryClient';
import { Layout } from '@/components/layout/Layout';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import { Dashboard } from '@/pages/Dashboard';
import { ExperimentList } from '@/pages/ExperimentList';
import { ExperimentNew } from '@/pages/ExperimentNew';
import { ExperimentDetails } from '@/pages/ExperimentDetails';
import { VulnerabilityReport } from '@/pages/VulnerabilityReport';
import { VulnerabilityDetails } from '@/pages/VulnerabilityDetails';
import { Analytics } from '@/pages/Analytics';
import ExperimentMonitor from '@/pages/ExperimentMonitor';
import { TemplatesPage } from '@/pages/TemplatesPage';
import { JailbreakTemplatesPage } from '@/pages/JailbreakTemplatesPage';
import { SettingsPage } from '@/pages/SettingsPage';
import { useThemeStore } from '@/store/themeStore';
import { useEffect } from 'react';

function AppContent() {
  const { theme } = useThemeStore();

  useEffect(() => {
    // Apply theme on mount
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/experiments" element={<ExperimentList />} />
        <Route path="/experiments/new" element={<ExperimentNew />} />
        <Route path="/experiments/:experimentId" element={<ExperimentDetails />} />
        <Route path="/experiments/:experimentId/monitor" element={<ExperimentMonitor />} />
        <Route path="/vulnerabilities" element={<VulnerabilityReport />} />
        <Route path="/vulnerabilities/:vulnerabilityId" element={<VulnerabilityDetails />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/templates" element={<TemplatesPage />} />
        <Route path="/jailbreak-templates" element={<JailbreakTemplatesPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </Layout>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AppContent />
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
