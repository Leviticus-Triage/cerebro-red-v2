/**
 * Settings page for configuring template repositories and other application settings.
 *
 * Allows users to:
 * - Add/edit/delete GitHub repositories for template updates
 * - View update history per repository
 * - Configure repository settings (extraction scripts, categories, etc.)
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api/client';
import { toast } from '@/lib/toast';
import { Plus, Edit, Trash2, RefreshCw, History } from 'lucide-react';

interface RepositoryConfig {
  name: string;
  url: string;
  path: string;
  extraction_script?: string;
  categories: string[];
  license: string;
  source: string;
}

interface UpdateHistory {
  repository: string;
  timestamp: string;
  templates_added: number;
  templates_updated: number;
  success: boolean;
  error?: string;
}

export function SettingsPage() {
  const queryClient = useQueryClient();
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isHistoryDialogOpen, setIsHistoryDialogOpen] = useState(false);
  const [editingRepo, setEditingRepo] = useState<RepositoryConfig | null>(null);
  const [selectedRepoForHistory, setSelectedRepoForHistory] = useState<string>('');
  const [newRepo, setNewRepo] = useState<RepositoryConfig>({
    name: '',
    url: '',
    path: '',
    extraction_script: '',
    categories: [],
    license: 'MIT',
    source: '',
  });

  // Fetch repositories and their status
  const { data: repositoriesData, isLoading: reposLoading } = useQuery({
    queryKey: ['template-repositories'],
    queryFn: async () => {
      // Get both repository list and status
      const [repos, status] = await Promise.all([
        apiClient.listTemplateRepositories(),
        apiClient.getJailbreakTemplateStatus(),
      ]);
      return {
        repositories: repos.repositories || {},
        status: status.repositories || {},
      };
    },
  });

  // Fetch update history
  const { data: historyData } = useQuery({
    queryKey: ['template-update-history', selectedRepoForHistory],
    queryFn: async () => {
      return apiClient.getRepositoryUpdateHistory(selectedRepoForHistory);
    },
    enabled: isHistoryDialogOpen && !!selectedRepoForHistory,
  });

  // Mutations
  const addRepoMutation = useMutation({
    mutationFn: async (repo: RepositoryConfig) => {
      return apiClient.addTemplateRepository(repo);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['template-repositories'] });
      setIsAddDialogOpen(false);
      setNewRepo({
        name: '',
        url: '',
        path: '',
        extraction_script: '',
        categories: [],
        license: 'MIT',
        source: '',
      });
      toast.success('Repository added successfully');
    },
    onError: (error: Error) => {
      toast.error(`Failed to add repository: ${error.message}`);
    },
  });

  const updateRepoMutation = useMutation({
    mutationFn: async (repo: RepositoryConfig) => {
      return apiClient.updateTemplateRepository(repo.name, {
        url: repo.url,
        path: repo.path,
        extraction_script: repo.extraction_script,
        categories: repo.categories,
        license: repo.license,
        source: repo.source,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['template-repositories'] });
      setIsEditDialogOpen(false);
      setEditingRepo(null);
      toast.success('Repository updated successfully');
    },
    onError: (error: Error) => {
      toast.error(`Failed to update repository: ${error.message}`);
    },
  });

  const deleteRepoMutation = useMutation({
    mutationFn: async (repoName: string) => {
      return apiClient.deleteTemplateRepository(repoName);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['template-repositories'] });
      toast.success('Repository deleted successfully');
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete repository: ${error.message}`);
    },
  });

  const updateSingleRepoMutation = useMutation({
    mutationFn: async (repoName: string) => {
      return apiClient.updateJailbreakTemplates(repoName, true);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['template-repositories'] });
      queryClient.invalidateQueries({ queryKey: ['jailbreak-templates'] });
      toast.success(
        `Repository updated! Added: ${data.templates_added || 0}, Updated: ${data.templates_updated || 0}`
      );
    },
    onError: (error: Error) => {
      toast.error(`Update failed: ${error.message}`);
    },
  });

  const repositories = repositoriesData?.repositories || {};
  const repoStatus = repositoriesData?.status || {};

  const handleAddRepo = () => {
    if (!newRepo.name || !newRepo.url || !newRepo.path) {
      toast.error('Name, URL, and path are required');
      return;
    }
    addRepoMutation.mutate(newRepo);
  };

  const handleEditRepo = () => {
    if (!editingRepo || !editingRepo.name || !editingRepo.url || !editingRepo.path) {
      toast.error('Name, URL, and path are required');
      return;
    }
    updateRepoMutation.mutate(editingRepo);
  };

  const handleDeleteRepo = (repoName: string) => {
    if (!confirm(`Delete repository "${repoName}"? This cannot be undone.`)) {
      return;
    }
    deleteRepoMutation.mutate(repoName);
  };

  const handleUpdateRepo = (repoName: string) => {
    if (!confirm(`Update templates from "${repoName}"? A backup will be created.`)) {
      return;
    }
    updateSingleRepoMutation.mutate(repoName);
  };

  const handleViewHistory = (repoName: string) => {
    setSelectedRepoForHistory(repoName);
    setIsHistoryDialogOpen(true);
  };

  if (reposLoading) {
    return <div className="p-6">Loading repositories...</div>;
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-gray-500 mt-1">
            Configure template repositories and application settings
          </p>
        </div>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Add Repository
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Add Template Repository</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Repository Name</Label>
                <Input
                  value={newRepo.name}
                  onChange={(e) => setNewRepo({ ...newRepo, name: e.target.value })}
                  placeholder="e.g., MyCustomRepo"
                />
              </div>
              <div>
                <Label>GitHub URL</Label>
                <Input
                  value={newRepo.url}
                  onChange={(e) => setNewRepo({ ...newRepo, url: e.target.value })}
                  placeholder="https://github.com/user/repo.git"
                />
              </div>
              <div>
                <Label>Local Path</Label>
                <Input
                  value={newRepo.path}
                  onChange={(e) => setNewRepo({ ...newRepo, path: e.target.value })}
                  placeholder="repo-name"
                />
              </div>
              <div>
                <Label>Extraction Script (optional)</Label>
                <Input
                  value={newRepo.extraction_script || ''}
                  onChange={(e) => setNewRepo({ ...newRepo, extraction_script: e.target.value })}
                  placeholder="backend/scripts/extract_templates.py"
                />
              </div>
              <div>
                <Label>Categories (comma-separated)</Label>
                <Input
                  value={newRepo.categories.join(', ')}
                  onChange={(e) =>
                    setNewRepo({
                      ...newRepo,
                      categories: e.target.value
                        .split(',')
                        .map((s) => s.trim())
                        .filter(Boolean),
                    })
                  }
                  placeholder="category1, category2, category3"
                />
              </div>
              <div>
                <Label>License</Label>
                <Input
                  value={newRepo.license}
                  onChange={(e) => setNewRepo({ ...newRepo, license: e.target.value })}
                  placeholder="MIT"
                />
              </div>
              <div>
                <Label>Source Name</Label>
                <Input
                  value={newRepo.source}
                  onChange={(e) => setNewRepo({ ...newRepo, source: e.target.value })}
                  placeholder="Source identifier"
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleAddRepo} disabled={addRepoMutation.isPending}>
                  Add Repository
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Repositories List */}
      <div className="grid grid-cols-1 gap-4">
        {Object.entries(repositories).map(([repoName, repoConfig]: [string, any]) => {
          const status = repoStatus[repoName] || {};
          const fullRepoConfig: RepositoryConfig = {
            name: repoName,
            url: repoConfig.url || '',
            path: repoConfig.path || '',
            extraction_script: repoConfig.extraction_script,
            categories: repoConfig.categories || [],
            license: repoConfig.license || 'MIT',
            source: repoConfig.source || repoName,
          };

          return (
            <Card key={repoName}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{repoName}</CardTitle>
                    <p className="text-sm text-gray-500 mt-1">{fullRepoConfig.url}</p>
                    <div className="flex gap-2 mt-2">
                      <Badge variant={status.exists ? 'default' : 'secondary'}>
                        {status.exists ? 'Cloned' : 'Not Cloned'}
                      </Badge>
                      {status.is_git && <Badge variant="outline">Git Repository</Badge>}
                      {status.branch && <Badge variant="outline">Branch: {status.branch}</Badge>}
                    </div>
                    {status.last_commit_date && (
                      <p className="text-sm text-gray-500 mt-2">
                        Last commit: {new Date(status.last_commit_date).toLocaleString()}
                      </p>
                    )}
                    {status.last_commit && (
                      <p className="text-xs text-gray-400 font-mono mt-1">
                        {status.last_commit.substring(0, 8)}
                      </p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" onClick={() => handleViewHistory(repoName)}>
                      <History className="w-4 h-4 mr-1" />
                      History
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleUpdateRepo(repoName)}
                      disabled={updateSingleRepoMutation.isPending}
                    >
                      <RefreshCw className="w-4 h-4 mr-1" />
                      Update
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setEditingRepo(fullRepoConfig);
                        setIsEditDialogOpen(true);
                      }}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => handleDeleteRepo(repoName)}>
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
            </Card>
          );
        })}
        {Object.keys(repositories).length === 0 && (
          <Card>
            <CardContent className="p-8 text-center text-gray-500">
              No repositories configured. Add a repository to get started.
            </CardContent>
          </Card>
        )}
      </div>

      {/* Edit Repository Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Repository</DialogTitle>
          </DialogHeader>
          {editingRepo && (
            <div className="space-y-4">
              <div>
                <Label>Repository Name</Label>
                <Input
                  value={editingRepo.name}
                  onChange={(e) => setEditingRepo({ ...editingRepo, name: e.target.value })}
                />
              </div>
              <div>
                <Label>GitHub URL</Label>
                <Input
                  value={editingRepo.url}
                  onChange={(e) => setEditingRepo({ ...editingRepo, url: e.target.value })}
                />
              </div>
              <div>
                <Label>Local Path</Label>
                <Input
                  value={editingRepo.path}
                  onChange={(e) => setEditingRepo({ ...editingRepo, path: e.target.value })}
                />
              </div>
              <div>
                <Label>Extraction Script (optional)</Label>
                <Input
                  value={editingRepo.extraction_script || ''}
                  onChange={(e) =>
                    setEditingRepo({ ...editingRepo, extraction_script: e.target.value })
                  }
                />
              </div>
              <div>
                <Label>Categories (comma-separated)</Label>
                <Input
                  value={editingRepo.categories.join(', ')}
                  onChange={(e) =>
                    setEditingRepo({
                      ...editingRepo,
                      categories: e.target.value
                        .split(',')
                        .map((s) => s.trim())
                        .filter(Boolean),
                    })
                  }
                />
              </div>
              <div>
                <Label>License</Label>
                <Input
                  value={editingRepo.license}
                  onChange={(e) => setEditingRepo({ ...editingRepo, license: e.target.value })}
                />
              </div>
              <div>
                <Label>Source Name</Label>
                <Input
                  value={editingRepo.source}
                  onChange={(e) => setEditingRepo({ ...editingRepo, source: e.target.value })}
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleEditRepo} disabled={updateRepoMutation.isPending}>
                  Save Changes
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* History Dialog */}
      <Dialog open={isHistoryDialogOpen} onOpenChange={setIsHistoryDialogOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Update History: {selectedRepoForHistory}</DialogTitle>
          </DialogHeader>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {historyData?.history?.map((entry: UpdateHistory, idx: number) => (
              <Card key={idx}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">
                        {new Date(entry.timestamp).toLocaleString()}
                      </div>
                      <div className="text-sm text-gray-500">
                        Added: {entry.templates_added} • Updated: {entry.templates_updated}
                      </div>
                      {entry.error && (
                        <div className="text-sm text-red-500 mt-1">{entry.error}</div>
                      )}
                    </div>
                    <Badge variant={entry.success ? 'default' : 'destructive'}>
                      {entry.success ? 'Success' : 'Failed'}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
            {(!historyData?.history || historyData.history.length === 0) && (
              <div className="text-center text-gray-500 py-8">No update history available</div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
