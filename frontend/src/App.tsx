/**
 * Copyright 2024-2026 Cerebro-Red v2 Contributors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

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
