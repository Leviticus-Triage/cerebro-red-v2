/**
 * Template selector component for experiment form.
 *
 * Allows loading saved templates into the experiment form.
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { useTemplates, useUseTemplate } from '@/hooks/useTemplates';
import type { ExperimentConfig } from '@/types/api';

interface TemplateSelectorProps {
  onTemplateLoad: (config: ExperimentConfig) => void;
}

export function TemplateSelector({ onTemplateLoad }: TemplateSelectorProps) {
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>('');
  const { data: templatesData, isLoading } = useTemplates(1, 100); // Load all templates
  const useTemplate = useUseTemplate();

  const handleLoadTemplate = async () => {
    if (!selectedTemplateId) return;

    try {
      const template = await useTemplate.mutateAsync(selectedTemplateId);
      onTemplateLoad(template.config);

      // Show success notification
      import('@/lib/toast')
        .then(({ toast }) => {
          toast.success(`Template "${template.name}" loaded successfully`);
        })
        .catch(() => {
          // Toast not available, use console
          console.log(`Template "${template.name}" loaded successfully`);
        });
    } catch (error) {
      import('@/lib/toast')
        .then(({ toast }) => {
          toast.error('Failed to load template');
        })
        .catch(() => {
          console.error('Failed to load template', error);
        });
    }
  };

  if (isLoading) {
    return <div className="text-sm text-gray-500">Loading templates...</div>;
  }

  const templates = templatesData?.items || [];

  if (templates.length === 0) {
    return (
      <Card>
        <CardContent className="py-4 text-center text-sm text-gray-500">
          No templates available. Create experiments and save them as templates.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Load from Template</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label>Select Template</Label>
          <select
            value={selectedTemplateId}
            onChange={(e) => setSelectedTemplateId(e.target.value)}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <option value="">-- Select a template --</option>
            {templates.map((template) => (
              <option key={template.template_id} value={template.template_id}>
                {template.name} ({template.config.strategies.length} strategies, used{' '}
                {template.usage_count || 0}x)
              </option>
            ))}
          </select>
        </div>

        {selectedTemplateId && (
          <div className="space-y-2">
            {(() => {
              const template = templates.find((t) => t.template_id === selectedTemplateId);
              if (!template) return null;

              return (
                <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-md space-y-2">
                  <p className="text-sm">{template.description || 'No description'}</p>
                  <div className="flex flex-wrap gap-1">
                    {template.tags.map((tag) => (
                      <Badge key={tag} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                  <div className="text-xs text-gray-500">
                    Target: {template.config.target_model_provider}/
                    {template.config.target_model_name}
                  </div>
                </div>
              );
            })()}
          </div>
        )}

        <Button
          onClick={handleLoadTemplate}
          disabled={!selectedTemplateId || useTemplate.isPending}
          className="w-full"
        >
          {useTemplate.isPending ? 'Loading...' : 'Load Template'}
        </Button>
      </CardContent>
    </Card>
  );
}
