/**
 * Jailbreak Templates management page.
 *
 * Allows users to:
 * - View all jailbreak templates by category
 * - Add new templates
 * - Edit existing templates
 * - Delete templates
 * - Import/Export templates
 * - Update templates from GitHub repositories (with backup)
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
// Using native HTML select instead of Select component
import { apiClient } from '@/lib/api/client';
import { toast } from '@/lib/toast';
import { Trash2, Edit, Plus, Download, Upload, RefreshCw, Archive } from 'lucide-react';

export function JailbreakTemplatesPage() {
  const queryClient = useQueryClient();
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isUpdateDialogOpen, setIsUpdateDialogOpen] = useState(false);
  const [isImportDialogOpen, setIsImportDialogOpen] = useState(false);
  const [isBackupDialogOpen, setIsBackupDialogOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<{
    category: string;
    index: number;
    template: string;
  } | null>(null);
  const [newTemplate, setNewTemplate] = useState({ category: '', template: '' });
  const [selectedRepository, setSelectedRepository] = useState<string>('');

  // Fetch categories
  const { data: categoriesData, isLoading: categoriesLoading } = useQuery({
    queryKey: ['jailbreak-categories'],
    queryFn: () => apiClient.getJailbreakCategories(),
  });

  // Fetch templates
  const { data: templatesData, isLoading: templatesLoading } = useQuery({
    queryKey: ['jailbreak-templates', selectedCategory, searchQuery],
    queryFn: () =>
      apiClient.getJailbreakTemplates(selectedCategory || undefined, searchQuery || undefined),
    enabled: true,
  });

  // Fetch repository status (for future use)
  // const { data: statusData } = useQuery({
  //   queryKey: ['jailbreak-status'],
  //   queryFn: () => apiClient.getJailbreakTemplateStatus(),
  // });

  // Fetch backups
  const { data: backupsData } = useQuery({
    queryKey: ['jailbreak-backups'],
    queryFn: () => apiClient.listJailbreakBackups(),
  });

  // Mutations
  const addTemplateMutation = useMutation({
    mutationFn: ({ category, template }: { category: string; template: string }) =>
      apiClient.addJailbreakTemplate(category, template),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jailbreak-templates'] });
      queryClient.invalidateQueries({ queryKey: ['jailbreak-categories'] });
      setIsAddDialogOpen(false);
      setNewTemplate({ category: '', template: '' });
      toast.success('Template added successfully');
    },
    onError: (error: Error) => {
      toast.error(`Failed to add template: ${error.message}`);
    },
  });

  const updateTemplateMutation = useMutation({
    mutationFn: ({
      category,
      index,
      template,
    }: {
      category: string;
      index: number;
      template: string;
    }) => apiClient.updateJailbreakTemplate(category, index, template),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jailbreak-templates'] });
      setIsEditDialogOpen(false);
      setEditingTemplate(null);
      toast.success('Template updated successfully');
    },
    onError: (error: Error) => {
      toast.error(`Failed to update template: ${error.message}`);
    },
  });

  const deleteTemplateMutation = useMutation({
    mutationFn: ({ category, index }: { category: string; index: number }) =>
      apiClient.deleteJailbreakTemplate(category, index),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jailbreak-templates'] });
      queryClient.invalidateQueries({ queryKey: ['jailbreak-categories'] });
      toast.success('Template deleted successfully');
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete template: ${error.message}`);
    },
  });

  const deleteCategoryMutation = useMutation({
    mutationFn: (category: string) => apiClient.deleteJailbreakCategory(category),
    onSuccess: (_, category) => {
      queryClient.invalidateQueries({ queryKey: ['jailbreak-templates'] });
      queryClient.invalidateQueries({ queryKey: ['jailbreak-categories'] });
      if (selectedCategory === category) {
        setSelectedCategory(null);
      }
      toast.success('Category deleted successfully');
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete category: ${error.message}`);
    },
  });

  const updateTemplatesMutation = useMutation({
    mutationFn: ({ repository, createBackup }: { repository?: string; createBackup: boolean }) =>
      apiClient.updateJailbreakTemplates(repository, createBackup),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['jailbreak-templates'] });
      queryClient.invalidateQueries({ queryKey: ['jailbreak-categories'] });
      queryClient.invalidateQueries({ queryKey: ['jailbreak-status'] });
      setIsUpdateDialogOpen(false);
      setSelectedRepository('');
      toast.success(
        `Update successful! Added: ${data.templates_added || data.total_templates_added || 0}, Updated: ${data.templates_updated || data.total_templates_updated || 0}`
      );
    },
    onError: (error: Error) => {
      toast.error(`Update failed: ${error.message}`);
    },
  });

  const importMutation = useMutation({
    mutationFn: ({ content, merge }: { content: string; merge: boolean }) =>
      apiClient.importJailbreakTemplates(content, merge),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['jailbreak-templates'] });
      queryClient.invalidateQueries({ queryKey: ['jailbreak-categories'] });
      setIsImportDialogOpen(false);
      toast.success(`Imported ${data.total_templates} templates successfully`);
    },
    onError: (error: Error) => {
      toast.error(`Import failed: ${error.message}`);
    },
  });

  const restoreMutation = useMutation({
    mutationFn: (backupPath: string) => apiClient.restoreJailbreakTemplates(backupPath),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jailbreak-templates'] });
      queryClient.invalidateQueries({ queryKey: ['jailbreak-categories'] });
      setIsBackupDialogOpen(false);
      toast.success('Templates restored from backup successfully');
    },
    onError: (error: Error) => {
      toast.error(`Restore failed: ${error.message}`);
    },
  });

  const handleExport = async (category?: string) => {
    try {
      const data = await apiClient.exportJailbreakTemplates(category);
      const blob = new Blob([JSON.stringify(data.data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `jailbreak-templates${category ? `-${category}` : ''}-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success('Templates exported successfully');
    } catch (error: any) {
      toast.error(`Export failed: ${error.message}`);
    }
  };

  const handleImportFile = async (file: File) => {
    try {
      const text = await file.text();
      const json = JSON.parse(text);
      importMutation.mutate({ content: JSON.stringify(json), merge: true });
    } catch (error: any) {
      toast.error(`Invalid JSON file: ${error.message}`);
    }
  };

  const handleUpdate = () => {
    if (
      !confirm(
        'This will update templates from GitHub repositories. A backup will be created automatically. Continue?'
      )
    ) {
      return;
    }
    updateTemplatesMutation.mutate({
      repository: selectedRepository || undefined,
      createBackup: true,
    });
  };

  const handleRestore = (backupPath: string) => {
    if (
      !confirm(
        'This will restore templates from backup. Current templates will be backed up first. Continue?'
      )
    ) {
      return;
    }
    restoreMutation.mutate(backupPath);
  };

  const categories = categoriesData?.categories || [];
  const templates = templatesData?.categories || {};

  if (categoriesLoading || templatesLoading) {
    return <div className="p-6">Loading templates...</div>;
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Jailbreak Templates</h1>
          <p className="text-gray-500 mt-1">Manage jailbreak attack templates</p>
        </div>
        <div className="flex gap-2">
          <Dialog open={isUpdateDialogOpen} onOpenChange={setIsUpdateDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" disabled={updateTemplatesMutation.isPending}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Update from Repos
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Update Templates from Repositories</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label>Repository (leave empty for all)</Label>
                  <select
                    value={selectedRepository}
                    onChange={(e) => setSelectedRepository(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                  >
                    <option value="">All repositories</option>
                    <option value="PyRIT">PyRIT</option>
                    <option value="L1B3RT4S">L1B3RT4S</option>
                    <option value="LLAMATOR">LLAMATOR</option>
                    <option value="Model-Inversion-Attack-ToolBox">
                      Model-Inversion-Attack-ToolBox
                    </option>
                  </select>
                </div>
                <div className="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded text-sm">
                  A backup will be created automatically before updating.
                </div>
                <Button
                  onClick={handleUpdate}
                  disabled={updateTemplatesMutation.isPending}
                  className="w-full"
                >
                  {updateTemplatesMutation.isPending ? 'Updating...' : 'Update Templates'}
                </Button>
              </div>
            </DialogContent>
          </Dialog>

          <Dialog open={isImportDialogOpen} onOpenChange={setIsImportDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Upload className="w-4 h-4 mr-2" />
                Import
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Import Templates</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label>JSON File</Label>
                  <Input
                    type="file"
                    accept=".json"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) handleImportFile(file);
                    }}
                  />
                </div>
              </div>
            </DialogContent>
          </Dialog>

          <Button variant="outline" onClick={() => handleExport()}>
            <Download className="w-4 h-4 mr-2" />
            Export All
          </Button>

          <Dialog open={isBackupDialogOpen} onOpenChange={setIsBackupDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Archive className="w-4 h-4 mr-2" />
                Backups
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Backup Management</DialogTitle>
              </DialogHeader>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {backupsData?.backups?.map((backup) => (
                  <Card key={backup.path}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium">{backup.filename}</div>
                          <div className="text-sm text-gray-500">
                            {new Date(backup.created_at).toLocaleString()} •{' '}
                            {(backup.size / 1024).toFixed(2)} KB
                          </div>
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleRestore(backup.path)}
                          disabled={restoreMutation.isPending}
                        >
                          Restore
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
                {(!backupsData?.backups || backupsData.backups.length === 0) && (
                  <div className="text-center text-gray-500 py-8">No backups available</div>
                )}
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="flex gap-4">
        <Input
          placeholder="Search templates..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1"
        />
        <select
          value={selectedCategory || ''}
          onChange={(e) => setSelectedCategory(e.target.value || null)}
          className="w-48 px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
        >
          <option value="">All categories</option>
          {categories.map((cat) => (
            <option key={cat.name} value={cat.name}>
              {cat.name} ({cat.template_count})
            </option>
          ))}
        </select>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-sm text-gray-500">Total Categories</div>
            <div className="text-2xl font-bold">{templatesData?.total_categories || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-sm text-gray-500">Total Templates</div>
            <div className="text-2xl font-bold">{templatesData?.total_templates || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-sm text-gray-500">Last Updated</div>
            <div className="text-sm font-medium">
              {templatesData?.last_updated
                ? new Date(templatesData.last_updated).toLocaleDateString()
                : 'N/A'}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-sm text-gray-500">Version</div>
            <div className="text-sm font-medium">{templatesData?.version || 'N/A'}</div>
          </CardContent>
        </Card>
      </div>

      {/* Categories List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {categories.map((category) => {
          const categoryData = templates[category.name];
          const templatesList = categoryData?.templates || [];

          return (
            <Card key={category.name}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{category.name}</CardTitle>
                    <p className="text-sm text-gray-500 mt-1">{category.description}</p>
                  </div>
                  <div className="flex gap-1">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => {
                        setNewTemplate({ category: category.name, template: '' });
                        setIsAddDialogOpen(true);
                      }}
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => handleExport(category.name)}>
                      <Download className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => {
                        if (
                          confirm(
                            `Delete category "${category.name}" and all ${templatesList.length} templates?`
                          )
                        ) {
                          deleteCategoryMutation.mutate(category.name);
                        }
                      }}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                <div className="flex gap-2 mt-2">
                  <Badge
                    variant={
                      category.severity === 'critical'
                        ? 'destructive'
                        : category.severity === 'high'
                          ? 'default'
                          : 'secondary'
                    }
                  >
                    {category.severity}
                  </Badge>
                  <Badge variant="outline">{templatesList.length} templates</Badge>
                  {category.source && <Badge variant="outline">{category.source}</Badge>}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {templatesList.map((template: string, index: number) => (
                    <div key={index} className="p-2 bg-gray-50 dark:bg-gray-800 rounded text-sm">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 truncate">{template.substring(0, 100)}...</div>
                        <div className="flex gap-1">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => {
                              setEditingTemplate({ category: category.name, index, template });
                              setIsEditDialogOpen(true);
                            }}
                          >
                            <Edit className="w-3 h-3" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => {
                              if (confirm('Delete this template?')) {
                                deleteTemplateMutation.mutate({ category: category.name, index });
                              }
                            }}
                          >
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                  {templatesList.length === 0 && (
                    <div className="text-center text-gray-500 py-4">
                      No templates in this category
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Add Template Dialog */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Add Template</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Category</Label>
              <Input
                value={newTemplate.category}
                onChange={(e) => setNewTemplate({ ...newTemplate, category: e.target.value })}
                placeholder="e.g., jailbreak_dan"
              />
            </div>
            <div>
              <Label>Template</Label>
              <Textarea
                value={newTemplate.template}
                onChange={(e) => setNewTemplate({ ...newTemplate, template: e.target.value })}
                placeholder="Enter template text. Use {original_prompt} as placeholder."
                rows={10}
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                Cancel
              </Button>
              <Button
                onClick={() => {
                  if (newTemplate.category && newTemplate.template) {
                    addTemplateMutation.mutate(newTemplate);
                  }
                }}
                disabled={
                  !newTemplate.category || !newTemplate.template || addTemplateMutation.isPending
                }
              >
                Add Template
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Edit Template Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Template</DialogTitle>
          </DialogHeader>
          {editingTemplate && (
            <div className="space-y-4">
              <div>
                <Label>Category</Label>
                <Input value={editingTemplate.category} disabled />
              </div>
              <div>
                <Label>Template</Label>
                <Textarea
                  value={editingTemplate.template}
                  onChange={(e) =>
                    setEditingTemplate({ ...editingTemplate, template: e.target.value })
                  }
                  rows={10}
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
                  Cancel
                </Button>
                <Button
                  onClick={() => {
                    if (editingTemplate.template) {
                      updateTemplateMutation.mutate(editingTemplate);
                    }
                  }}
                  disabled={!editingTemplate.template || updateTemplateMutation.isPending}
                >
                  Save Changes
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
