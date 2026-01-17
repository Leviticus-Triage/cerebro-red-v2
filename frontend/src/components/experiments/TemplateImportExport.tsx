/**
 * Template Import/Export component.
 *
 * Allows users to export templates as JSON files and import them back.
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Download, Upload } from 'lucide-react';
import type { ExperimentTemplate } from '@/types/api';

interface TemplateImportExportProps {
  templates: ExperimentTemplate[];
  onImport: (
    template: Omit<ExperimentTemplate, 'template_id' | 'created_at' | 'updated_at' | 'usage_count'>
  ) => void;
}

export function TemplateImportExport({ templates, onImport }: TemplateImportExportProps) {
  const [importing, setImporting] = useState(false);

  const handleExport = (template: ExperimentTemplate) => {
    // Create exportable template (remove server-side fields)
    const exportData = {
      name: template.name,
      description: template.description,
      config: template.config,
      tags: template.tags,
      is_public: template.is_public,
      created_by: template.created_by,
      version: '2.0.0',
      exported_at: new Date().toISOString(),
    };

    // Create blob and download
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cerebro-template-${template.name.replace(/[^a-z0-9]/gi, '-').toLowerCase()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleExportAll = () => {
    const exportData = {
      templates: templates.map((t) => ({
        name: t.name,
        description: t.description,
        config: t.config,
        tags: t.tags,
        is_public: t.is_public,
        created_by: t.created_by,
      })),
      version: '2.0.0',
      exported_at: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cerebro-templates-all-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setImporting(true);
    const reader = new FileReader();

    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const data = JSON.parse(content);

        // Check if it's a single template or multiple
        if (data.templates && Array.isArray(data.templates)) {
          // Multiple templates
          data.templates.forEach((template: any) => {
            onImport({
              name: template.name,
              description: template.description,
              config: template.config,
              tags: template.tags || [],
              is_public: template.is_public || false,
              created_by: template.created_by || 'imported',
            });
          });
          alert(`Successfully imported ${data.templates.length} templates!`);
        } else if (data.name && data.config) {
          // Single template
          onImport({
            name: data.name,
            description: data.description,
            config: data.config,
            tags: data.tags || [],
            is_public: data.is_public || false,
            created_by: data.created_by || 'imported',
          });
          alert(`Successfully imported template: ${data.name}`);
        } else {
          throw new Error('Invalid template format');
        }
      } catch (error) {
        console.error('Import error:', error);
        alert('Failed to import template. Please check the file format.');
      } finally {
        setImporting(false);
        // Reset file input
        event.target.value = '';
      }
    };

    reader.onerror = () => {
      alert('Failed to read file');
      setImporting(false);
    };

    reader.readAsText(file);
  };

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">Import / Export Templates</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Import */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-300">Import Template</label>
          <div className="flex gap-2">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => document.getElementById('template-import')?.click()}
              disabled={importing}
            >
              <Upload className="w-4 h-4 mr-2" />
              {importing ? 'Importing...' : 'Import from JSON'}
            </Button>
            <input
              id="template-import"
              type="file"
              accept=".json"
              onChange={handleImport}
              className="hidden"
            />
          </div>
          <p className="text-xs text-slate-400">
            Import templates created by AI or exported from other instances
          </p>
        </div>

        {/* Export */}
        {templates.length > 0 && (
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Export Templates</label>
            <div className="space-y-2">
              <Button variant="outline" className="w-full" onClick={handleExportAll}>
                <Download className="w-4 h-4 mr-2" />
                Export All Templates ({templates.length})
              </Button>

              <div className="max-h-40 overflow-y-auto space-y-1">
                {templates.map((template) => (
                  <button
                    key={template.template_id}
                    onClick={() => handleExport(template)}
                    className="w-full text-left px-3 py-2 text-sm rounded bg-slate-700 hover:bg-slate-600 transition-colors flex items-center justify-between"
                  >
                    <span className="truncate">{template.name}</span>
                    <Download className="w-3 h-3 flex-shrink-0 ml-2" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {templates.length === 0 && (
          <p className="text-sm text-slate-400 text-center py-4">
            No templates to export. Create some templates first!
          </p>
        )}
      </CardContent>
    </Card>
  );
}
