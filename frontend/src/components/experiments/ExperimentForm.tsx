/**
 * Experiment creation form component.
 */

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AttackStrategyType, LLMProvider, ExperimentConfig } from '@/types/api';
import { TemplateSelector } from './TemplateSelector';
import { TemplateImportExport } from './TemplateImportExport';
import { VerbositySelector } from './VerbositySelector';
import { useCreateTemplate, useTemplates } from '@/hooks/useTemplates';

// Simple UUID generator (crypto.randomUUID if available, fallback otherwise)
function generateUUID(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // Fallback UUID v4 generator
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

interface ExperimentFormProps {
  onSubmit: (data: any) => void;
  isLoading?: boolean;
  initialConfig?: ExperimentConfig;  // NEW: For template loading
}

export function ExperimentForm({ onSubmit, isLoading, initialConfig }: ExperimentFormProps) {
  const createTemplate = useCreateTemplate();
  const { data: templatesData } = useTemplates(1, 100);
  
  const [formData, setFormData] = useState({
    name: initialConfig?.name || '',
    description: initialConfig?.description || '',
    target_model_provider: initialConfig?.target_model_provider || LLMProvider.OLLAMA,
    target_model_name: initialConfig?.target_model_name || '',
    attacker_model_provider: initialConfig?.attacker_model_provider || LLMProvider.OLLAMA,
    attacker_model_name: initialConfig?.attacker_model_name || '',
    judge_model_provider: initialConfig?.judge_model_provider || LLMProvider.OLLAMA,
    judge_model_name: initialConfig?.judge_model_name || '',
    initial_prompts: initialConfig?.initial_prompts || [''],
    strategies: initialConfig?.strategies || [] as AttackStrategyType[],
    max_iterations: initialConfig?.max_iterations || 20,
    max_concurrent_attacks: initialConfig?.max_concurrent_attacks || 5,
    success_threshold: initialConfig?.success_threshold || 7.0,
    timeout_seconds: initialConfig?.timeout_seconds || 3600,
    verbosity: 2, // Default verbosity level
  });

  // Update form when initialConfig changes (template loaded)
  useEffect(() => {
    if (initialConfig) {
      setFormData({
        name: initialConfig.name,
        description: initialConfig.description || '',
        target_model_provider: initialConfig.target_model_provider,
        target_model_name: initialConfig.target_model_name,
        attacker_model_provider: initialConfig.attacker_model_provider,
        attacker_model_name: initialConfig.attacker_model_name,
        judge_model_provider: initialConfig.judge_model_provider,
        judge_model_name: initialConfig.judge_model_name,
        initial_prompts: initialConfig.initial_prompts,
        strategies: initialConfig.strategies,
        max_iterations: initialConfig.max_iterations,
        max_concurrent_attacks: initialConfig.max_concurrent_attacks,
        success_threshold: initialConfig.success_threshold,
        timeout_seconds: initialConfig.timeout_seconds,
        verbosity: 2, // Default verbosity
      });
    }
  }, [initialConfig]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const config = {
      experiment_id: generateUUID(),
      name: formData.name,
      description: formData.description || undefined,
      target_model_provider: formData.target_model_provider,
      target_model_name: formData.target_model_name,
      attacker_model_provider: formData.attacker_model_provider,
      attacker_model_name: formData.attacker_model_name,
      judge_model_provider: formData.judge_model_provider,
      judge_model_name: formData.judge_model_name,
      initial_prompts: formData.initial_prompts.filter(p => p.trim()),
      strategies: formData.strategies,
      max_iterations: formData.max_iterations,
      max_concurrent_attacks: formData.max_concurrent_attacks,
      success_threshold: formData.success_threshold,
      timeout_seconds: formData.timeout_seconds,
    };

    onSubmit(config);
  };

  const toggleStrategy = (strategy: AttackStrategyType) => {
    setFormData(prev => ({
      ...prev,
      strategies: prev.strategies.includes(strategy)
        ? prev.strategies.filter(s => s !== strategy)
        : [...prev.strategies, strategy],
    }));
  };

  const addPrompt = () => {
    setFormData(prev => ({
      ...prev,
      initial_prompts: [...prev.initial_prompts, ''],
    }));
  };

  const updatePrompt = (index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      initial_prompts: prev.initial_prompts.map((p, i) => i === index ? value : p),
    }));
  };

  const handleSaveAsTemplate = async () => {
    // Validate required fields
    if (!formData.name || !formData.target_model_name || !formData.attacker_model_name || !formData.judge_model_name) {
      alert('Please fill in all required fields (Experiment Name, Target Model, Attacker Model, Judge Model) before saving as template.');
      return;
    }
    
    if (formData.strategies.length === 0) {
      alert('Please select at least one attack strategy before saving as template.');
      return;
    }
    
    if (formData.initial_prompts.filter(p => p.trim()).length === 0) {
      alert('Please add at least one initial prompt before saving as template.');
      return;
    }
    
    const templateName = prompt('Enter template name:');
    if (!templateName) return;
    
    const templateDescription = prompt('Enter template description (optional):');
    const tagsInput = prompt('Enter tags (comma-separated, optional):');
    
    const tags = tagsInput ? tagsInput.split(',').map(t => t.trim()).filter(Boolean) : [];
    
    try {
      await createTemplate.mutateAsync({
        name: templateName,
        description: templateDescription || undefined,
        config: {
          experiment_id: generateUUID(),
          name: formData.name,
          description: formData.description || undefined,
          target_model_provider: formData.target_model_provider,
          target_model_name: formData.target_model_name,
          attacker_model_provider: formData.attacker_model_provider,
          attacker_model_name: formData.attacker_model_name,
          judge_model_provider: formData.judge_model_provider,
          judge_model_name: formData.judge_model_name,
          initial_prompts: formData.initial_prompts.filter(p => p.trim()),
          strategies: formData.strategies,
          max_iterations: formData.max_iterations,
          max_concurrent_attacks: formData.max_concurrent_attacks,
          success_threshold: formData.success_threshold,
          timeout_seconds: formData.timeout_seconds,
        },
        tags,
        is_public: false,
      });
      
      import('@/lib/toast').then(({ toast }) => {
        toast.success('Template saved successfully');
      }).catch(() => {
        console.log('Template saved successfully');
      });
    } catch (error) {
      import('@/lib/toast').then(({ toast }) => {
        toast.error('Failed to save template');
      }).catch(() => {
        console.error('Failed to save template', error);
      });
    }
  };

  const handleTemplateLoad = (config: ExperimentConfig) => {
    setFormData({
      name: config.name,
      description: config.description || '',
      target_model_provider: config.target_model_provider,
      target_model_name: config.target_model_name,
      attacker_model_provider: config.attacker_model_provider,
      attacker_model_name: config.attacker_model_name,
      judge_model_provider: config.judge_model_provider,
      judge_model_name: config.judge_model_name,
      initial_prompts: config.initial_prompts,
      strategies: config.strategies,
      max_iterations: config.max_iterations,
      max_concurrent_attacks: config.max_concurrent_attacks,
      success_threshold: config.success_threshold,
      timeout_seconds: config.timeout_seconds,
      verbosity: 2, // Default verbosity
    });
  };

  const handleTemplateImport = async (template: any) => {
    try {
      await createTemplate.mutateAsync(template);
      import('@/lib/toast').then(({ toast }) => {
        toast.success(`Template "${template.name}" imported successfully`);
      }).catch(() => {
        console.log(`Template "${template.name}" imported successfully`);
      });
    } catch (error) {
      import('@/lib/toast').then(({ toast }) => {
        toast.error('Failed to import template');
      }).catch(() => {
        console.error('Failed to import template', error);
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Template Selector */}
      <TemplateSelector onTemplateLoad={handleTemplateLoad} />
      
      {/* Import/Export */}
      <TemplateImportExport 
        templates={templatesData?.items || []}
        onImport={handleTemplateImport}
      />
      
      {/* Verbosity Level */}
      <VerbositySelector 
        value={formData.verbosity}
        onChange={(value) => setFormData(prev => ({ ...prev, verbosity: value }))}
      />
      
      {/* Save as Template Button */}
      <div className="flex justify-end">
        <Button
          type="button"
          variant="outline"
          onClick={handleSaveAsTemplate}
          disabled={createTemplate.isPending}
        >
          {createTemplate.isPending ? 'Saving...' : 'Save as Template'}
        </Button>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Basic Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Experiment Name *</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              required
              placeholder="e.g., LLM Safety Test - Qwen3"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Optional description of the experiment"
              rows={3}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Model Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Target Model Provider</Label>
              <Select
                value={formData.target_model_provider}
                onChange={(e) => setFormData(prev => ({ ...prev, target_model_provider: e.target.value as LLMProvider }))}
              >
                {Object.values(LLMProvider).map((provider) => (
                  <option key={provider} value={provider}>{provider}</option>
                ))}
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Target Model Name *</Label>
              <Input
                value={formData.target_model_name}
                onChange={(e) => setFormData(prev => ({ ...prev, target_model_name: e.target.value }))}
                required
                placeholder="e.g., qwen3:8b"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Attacker Model Provider</Label>
              <Select
                value={formData.attacker_model_provider}
                onChange={(e) => setFormData(prev => ({ ...prev, attacker_model_provider: e.target.value as LLMProvider }))}
              >
                {Object.values(LLMProvider).map((provider) => (
                  <option key={provider} value={provider}>{provider}</option>
                ))}
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Attacker Model Name *</Label>
              <Input
                value={formData.attacker_model_name}
                onChange={(e) => setFormData(prev => ({ ...prev, attacker_model_name: e.target.value }))}
                required
                placeholder="e.g., qwen3:8b"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Judge Model Provider</Label>
              <Select
                value={formData.judge_model_provider}
                onChange={(e) => setFormData(prev => ({ ...prev, judge_model_provider: e.target.value as LLMProvider }))}
              >
                {Object.values(LLMProvider).map((provider) => (
                  <option key={provider} value={provider}>{provider}</option>
                ))}
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Judge Model Name *</Label>
              <Input
                value={formData.judge_model_name}
                onChange={(e) => setFormData(prev => ({ ...prev, judge_model_name: e.target.value }))}
                required
                placeholder="e.g., qwen3:14b"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Initial Prompts *</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {formData.initial_prompts.map((prompt, index) => (
            <div key={index} className="space-y-2">
              <Label>Prompt {index + 1}</Label>
              <Textarea
                value={prompt}
                onChange={(e) => updatePrompt(index, e.target.value)}
                placeholder="Enter the initial prompt to test"
                rows={3}
              />
            </div>
          ))}
          <Button type="button" variant="outline" onClick={addPrompt}>
            Add Prompt
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Attack Strategies *</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-2">
            {Object.values(AttackStrategyType).map((strategy) => (
              <label key={strategy} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.strategies.includes(strategy)}
                  onChange={() => toggleStrategy(strategy)}
                  className="rounded"
                />
                <span className="text-sm">{strategy.replace(/_/g, ' ')}</span>
              </label>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Advanced Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Max Iterations</Label>
              <Input
                type="number"
                min={1}
                max={100}
                value={formData.max_iterations}
                onChange={(e) => setFormData(prev => ({ ...prev, max_iterations: parseInt(e.target.value) || 20 }))}
              />
            </div>
            <div className="space-y-2">
              <Label>Success Threshold</Label>
              <Input
                type="number"
                min={0}
                max={10}
                step="0.1"
                value={formData.success_threshold}
                onChange={(e) => setFormData(prev => ({ ...prev, success_threshold: parseFloat(e.target.value) || 7.0 }))}
              />
            </div>
            <div className="space-y-2">
              <Label>Timeout (seconds)</Label>
              <Input
                type="number"
                min={1}
                value={formData.timeout_seconds}
                onChange={(e) => setFormData(prev => ({ ...prev, timeout_seconds: parseInt(e.target.value) || 3600 }))}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Button type="submit" disabled={isLoading} className="w-full">
        {isLoading ? 'Creating...' : 'Create Experiment'}
      </Button>
    </form>
  );
}

