/**
 * Templates management page.
 * 
 * Allows users to:
 * - View all saved templates
 * - Create new templates
 * - Edit existing templates
 * - Delete templates
 * - Load templates into experiment form
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useTemplates, useDeleteTemplate } from '@/hooks/useTemplates';
import { ExperimentTemplate } from '@/types/api';

export function TemplatesPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [searchTags, setSearchTags] = useState('');
  
  const { data, isLoading, error } = useTemplates(page, 20, {
    tags: searchTags || undefined
  });
  const deleteTemplate = useDeleteTemplate();

  const handleDelete = async (templateId: string) => {
    if (confirm('Are you sure you want to delete this template?')) {
      await deleteTemplate.mutateAsync(templateId);
    }
  };

  const handleUse = (template: ExperimentTemplate) => {
    // Navigate to experiment creation with template data
    navigate('/experiments/new', { state: { template } });
  };

  if (isLoading) return <div>Loading templates...</div>;
  if (error) return <div>Error loading templates: {error.message}</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Experiment Templates</h1>
        <Button onClick={() => navigate('/experiments/new')}>
          Create Experiment (Save as Template)
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filter Templates</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label>Search by Tags (comma-separated)</Label>
            <Input
              value={searchTags}
              onChange={(e) => setSearchTags(e.target.value)}
              placeholder="e.g., jailbreak, owasp-llm01"
            />
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data?.items.map((template) => (
          <Card key={template.template_id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="flex justify-between items-start">
                <span className="truncate">{template.name}</span>
                {template.is_public && <Badge variant="outline">Public</Badge>}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {template.description || 'No description'}
              </p>
              
              <div className="space-y-2">
                <div className="text-xs text-gray-500">
                  <strong>Strategies:</strong> {template.config.strategies.length}
                </div>
                <div className="text-xs text-gray-500">
                  <strong>Prompts:</strong> {template.config.initial_prompts.length}
                </div>
                <div className="text-xs text-gray-500">
                  <strong>Used:</strong> {template.usage_count} times
                </div>
              </div>

              {template.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {template.tags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>
              )}

              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={() => handleUse(template)}
                  className="flex-1"
                >
                  Use Template
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    // Load template into experiment form for editing
                    navigate('/experiments/new', { state: { template } });
                  }}
                >
                  Edit
                </Button>
                <Button
                  size="sm"
                  variant="destructive"
                  onClick={() => handleDelete(template.template_id!)}
                >
                  Delete
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {data && data.total === 0 && (
        <Card>
          <CardContent className="py-8 text-center text-gray-500">
            No templates found. Create your first template to get started.
          </CardContent>
        </Card>
      )}

      {data && data.total > 20 && (
        <div className="flex justify-center gap-2">
          <Button
            variant="outline"
            disabled={page === 1}
            onClick={() => setPage(p => p - 1)}
          >
            Previous
          </Button>
          <span className="py-2 px-4">
            Page {page} of {Math.ceil(data.total / 20)}
          </span>
          <Button
            variant="outline"
            disabled={page >= Math.ceil(data.total / 20)}
            onClick={() => setPage(p => p + 1)}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
