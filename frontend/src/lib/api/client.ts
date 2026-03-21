import axios, { type AxiosInstance } from 'axios';
import type {
  ExperimentConfig,
  ExperimentListResponse,
  ExperimentResponse,
  ExperimentTemplate,
  ExperimentTemplateCreate,
  ExperimentTemplateListResponse,
  ExperimentTemplateUpdate,
} from '@/types/api';

export const DEFAULT_PAGE_SIZE = 20;

function getBase(): string {
  const v = import.meta.env.VITE_API_BASE_URL;
  if (v) return v.replace(/\/$/, '');
  return '';
}

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${getBase()}/api/v1`,
      headers: { 'Content-Type': 'application/json' },
      timeout: 120_000,
    });
    const key = localStorage.getItem('api_key');
    if (key) {
      this.client.defaults.headers.common['X-API-Key'] = key;
    }
  }

  setApiKey(key: string | null): void {
    if (key) {
      localStorage.setItem('api_key', key);
      this.client.defaults.headers.common['X-API-Key'] = key;
    } else {
      localStorage.removeItem('api_key');
      delete this.client.defaults.headers.common['X-API-Key'];
    }
  }

  clearApiKey(): void {
    this.setApiKey(null);
  }

  async healthCheck(): Promise<unknown> {
    const { data } = await axios.get(`${getBase() || ''}/health`);
    return data;
  }

  async getExperiments(page = 1, pageSize = DEFAULT_PAGE_SIZE): Promise<ExperimentListResponse> {
    const { data } = await this.client.get<ExperimentListResponse>('/experiments', {
      params: { page, page_size: pageSize },
    });
    return data;
  }

  async getExperiment(id: string): Promise<ExperimentResponse> {
    const { data } = await this.client.get<ExperimentResponse>(`/experiments/${id}`);
    return data;
  }

  async createExperiment(config: ExperimentConfig): Promise<ExperimentResponse> {
    const { data } = await this.client.post<ExperimentResponse>('/experiments', {
      experiment_config: config,
    });
    return data;
  }

  async deleteExperiment(id: string): Promise<void> {
    await this.client.delete(`/experiments/${id}`);
  }

  async startScan(config: ExperimentConfig): Promise<unknown> {
    const { data } = await this.client.post('/scan/start', { experiment_config: config });
    return data;
  }

  async getScanStatus(id: string): Promise<unknown> {
    const { data } = await this.client.get(`/scan/${id}/status`);
    return data;
  }

  async pauseScan(id: string): Promise<unknown> {
    const { data } = await this.client.post(`/scan/${id}/pause`);
    return data;
  }

  async resumeScan(id: string): Promise<unknown> {
    const { data } = await this.client.post(`/scan/${id}/resume`);
    return data;
  }

  async cancelScan(id: string): Promise<unknown> {
    const { data } = await this.client.post(`/scan/${id}/cancel`);
    return data;
  }

  async repeatExperiment(id: string): Promise<ExperimentResponse> {
    const { data } = await this.client.post<ExperimentResponse>(`/experiments/${id}/repeat`);
    return data;
  }

  async getExperimentIterations(id: string): Promise<unknown> {
    const { data } = await this.client.get(`/experiments/${id}/iterations`);
    return data;
  }

  async getExperimentStatistics(id: string): Promise<unknown> {
    const { data } = await this.client.get(`/experiments/${id}/statistics`);
    return data;
  }

  async getExperimentLogs(id: string): Promise<unknown> {
    const { data } = await this.client.get(`/experiments/${id}/logs`);
    return data;
  }

  async getExperimentResults(id: string): Promise<unknown> {
    const { data } = await this.client.get(`/experiments/${id}/results`);
    return data;
  }

  async getVulnerabilities(filters: Record<string, string>): Promise<unknown> {
    const { data } = await this.client.get('/vulnerabilities', { params: filters });
    return data;
  }

  async getVulnerability(id: string): Promise<unknown> {
    const { data } = await this.client.get(`/vulnerabilities/${id}`);
    return data;
  }

  async getVulnerabilityStatistics(): Promise<unknown> {
    const { data } = await this.client.get('/vulnerabilities/statistics/summary');
    return data;
  }

  async getTemplates(
    page: number,
    pageSize: number,
    filters?: Record<string, string>
  ): Promise<ExperimentTemplateListResponse> {
    const { data } = await this.client.get<ExperimentTemplateListResponse>('/templates', {
      params: { page, page_size: pageSize, ...filters },
    });
    return data;
  }

  async getTemplate(id: string): Promise<ExperimentTemplate> {
    const { data } = await this.client.get<ExperimentTemplate>(`/templates/${id}`);
    return data;
  }

  async createTemplate(t: ExperimentTemplateCreate): Promise<ExperimentTemplate> {
    const { data } = await this.client.post<ExperimentTemplate>('/templates', t);
    return data;
  }

  async updateTemplate(id: string, u: ExperimentTemplateUpdate): Promise<ExperimentTemplate> {
    const { data } = await this.client.put<ExperimentTemplate>(`/templates/${id}`, u);
    return data;
  }

  async deleteTemplate(id: string): Promise<void> {
    await this.client.delete(`/templates/${id}`);
  }

  async useTemplate(id: string): Promise<unknown> {
    const { data } = await this.client.post(`/templates/${id}/use`);
    return data;
  }

  async listTemplateRepositories(): Promise<unknown[]> {
    const { data } = await this.client.get<unknown[]>('/templates/repositories');
    return Array.isArray(data) ? data : [];
  }

  async getJailbreakTemplateStatus(): Promise<unknown> {
    const { data } = await this.client.get('/jailbreak-templates/status');
    return data;
  }

  async getRepositoryUpdateHistory(repo: string): Promise<unknown> {
    const { data } = await this.client.get(
      `/templates/repositories/${encodeURIComponent(repo)}/history`
    );
    return data;
  }

  async addTemplateRepository(repo: { name: string; url: string }): Promise<unknown> {
    const { data } = await this.client.post('/templates/repositories', repo);
    return data;
  }

  async updateTemplateRepository(name: string, body: Record<string, unknown>): Promise<unknown> {
    const { data } = await this.client.put(
      `/templates/repositories/${encodeURIComponent(name)}`,
      body
    );
    return data;
  }

  async deleteTemplateRepository(name: string): Promise<void> {
    await this.client.delete(`/templates/repositories/${encodeURIComponent(name)}`);
  }

  async updateJailbreakTemplates(repo: string, backup?: boolean): Promise<unknown> {
    const { data } = await this.client.post('/jailbreak-templates/update', {
      repository: repo,
      create_backup: backup,
    });
    return data;
  }

  async getJailbreakCategories(): Promise<string[]> {
    const { data } = await this.client.get<{ categories?: string[] }>(
      '/jailbreak-templates/categories'
    );
    return data.categories ?? [];
  }

  async getJailbreakTemplates(category?: string, search?: string): Promise<unknown> {
    const { data } = await this.client.get('/jailbreak-templates', {
      params: { category, search },
    });
    return data;
  }

  async listJailbreakBackups(): Promise<unknown[]> {
    const { data } = await this.client.get<unknown[]>('/jailbreak-templates/backups');
    return Array.isArray(data) ? data : [];
  }

  async addJailbreakTemplate(
    category: string,
    template: Record<string, unknown>
  ): Promise<unknown> {
    const { data } = await this.client.post(
      `/jailbreak-templates/${encodeURIComponent(category)}`,
      template
    );
    return data;
  }

  async updateJailbreakTemplate(
    category: string,
    index: number,
    template: Record<string, unknown>
  ): Promise<unknown> {
    const { data } = await this.client.put(
      `/jailbreak-templates/${encodeURIComponent(category)}/${index}`,
      template
    );
    return data;
  }

  async deleteJailbreakTemplate(category: string, index: number): Promise<void> {
    await this.client.delete(`/jailbreak-templates/${encodeURIComponent(category)}/${index}`);
  }

  async deleteJailbreakCategory(category: string): Promise<void> {
    await this.client.delete(`/jailbreak-templates/category/${encodeURIComponent(category)}`);
  }

  async importJailbreakTemplates(content: string, merge: boolean): Promise<unknown> {
    const { data } = await this.client.post('/jailbreak-templates/import', {
      content,
      merge,
    });
    return data;
  }

  async restoreJailbreakTemplates(backupPath: string): Promise<unknown> {
    const { data } = await this.client.post('/jailbreak-templates/restore', {
      backup_path: backupPath,
    });
    return data;
  }

  async exportJailbreakTemplates(category?: string): Promise<unknown> {
    const { data } = await this.client.get('/jailbreak-templates/export', {
      params: category ? { category } : {},
    });
    return data;
  }
}

export const apiClient = new ApiClient();
