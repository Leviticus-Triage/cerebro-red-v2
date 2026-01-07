/**
 * LiveLogPanel - Structured real-time log viewer with tab navigation
 * 
 * Displays streaming logs in 6 separate tabs:
 * - LLM Requests: All LLM request prompts with syntax highlighting
 * - LLM Responses: All LLM responses with latency and token counts
 * - Judge Evaluations: Judge scores, reasoning, and sub-scores
 * - Tasks: Task queue with status and dependencies
 * - Code Flow: Execution flow events with parameters/results
 * - Errors: Error messages with context
 */

import React, { useRef, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import type { LiveLogEntry, TaskQueueItem, CodeFlowEvent } from '@/types/api';

interface LiveLogPanelProps {
  logs: LiveLogEntry[];
  tasks?: TaskQueueItem[];
  codeFlowEvents?: CodeFlowEvent[];
  onExport?: (data: unknown[], format: 'json' | 'csv') => void;
  verbosity?: number; // Current verbosity level for visual indicators
}

// Helper Functions
const formatTime = (timestamp: string) => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('de-DE', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

const extractIteration = (log: LiveLogEntry | CodeFlowEvent) => {
  if ('iteration' in log && log.iteration !== undefined) {
    return log.iteration.toString();
  }
  const match = 'content' in log ? log.content.match(/iteration (\d+)/i) : null;
  return match ? match[1] : '-';
};

const getRoleBadgeColor = (role?: string) => {
  switch (role) {
    case 'attacker': return 'bg-red-900/50 text-red-400 border-red-700';
    case 'target': return 'bg-blue-900/50 text-blue-400 border-blue-700';
    case 'judge': return 'bg-amber-900/50 text-amber-400 border-amber-700';
    default: return 'bg-slate-800 text-slate-400';
  }
};

const getStatusBadge = (status: string) => {
  const config: Record<string, { color: string }> = {
    queued: { color: 'bg-slate-800 text-slate-400' },
    running: { color: 'bg-cyan-900/50 text-cyan-400' },
    completed: { color: 'bg-green-900/30 text-green-400' },
    failed: { color: 'bg-red-900/30 text-red-400' },
  };
  return config[status] || config.queued;
};

const getEventIcon = (_type: string) => {
  // Removed emojis for professional appearance
  return '';
};

const getScoreColor = (score: number) => {
  if (score >= 7) return 'text-green-400 bg-green-950/30';
  if (score >= 4) return 'text-yellow-400 bg-yellow-950/30';
  return 'text-red-400 bg-red-950/30';
};

// Helper function for keyboard navigation
const createKeyboardHandler = (toggleExpand: (id: string) => void, id: string) => {
  return (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      toggleExpand(id);
    }
  };
};

// Helper function for copy button
const createCopyButton = (content: string) => {
  return (
    <button
      onClick={(e) => {
        e.stopPropagation();
        navigator.clipboard.writeText(content).catch(err => {
          console.error('Failed to copy:', err);
        });
      }}
      className="px-2 py-1 text-xs bg-cyan-900/30 hover:bg-cyan-800/50 text-cyan-400 rounded transition-colors mb-2"
      title="Copy to clipboard"
    >
      Copy
    </button>
  );
};

// Table Components
const RequestsTable: React.FC<{
  logs: LiveLogEntry[];
  expandedRows: Set<string>;
  toggleExpand: (id: string) => void;
}> = ({ logs, expandedRows, toggleExpand }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div ref={containerRef} className="h-full overflow-y-auto w-full">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[80px]">Time</TableHead>
            <TableHead className="w-[80px]">Iteration</TableHead>
            <TableHead className="w-[100px]">Role</TableHead>
            <TableHead>Prompt</TableHead>
            <TableHead className="w-[150px]">Model</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {logs.map((log) => {
            const isExpanded = expandedRows.has(log.id);
            const roleColor = getRoleBadgeColor(log.role);
            const promptText = log.metadata?.prompt || log.content;

            return (
              <TableRow
                key={log.id}
                className="cursor-pointer hover:bg-slate-800/50 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                onClick={() => toggleExpand(log.id)}
                onKeyPress={createKeyboardHandler(toggleExpand, log.id)}
                tabIndex={0}
              >
                <TableCell className="font-mono text-xs text-slate-500">
                  {formatTime(log.timestamp)}
                </TableCell>
                <TableCell className="text-center text-slate-400">
                  {extractIteration(log)}
                </TableCell>
                <TableCell>
                  {log.role && (
                    <Badge className={roleColor}>
                      {log.role.toUpperCase()}
                    </Badge>
                  )}
                </TableCell>
                <TableCell className="font-mono text-sm">
                  {isExpanded ? (
                    <div>
                      <div className="flex justify-end">
                        {createCopyButton(promptText)}
                      </div>
                      <SyntaxHighlighter
                        language="text"
                        style={vscDarkPlus}
                        customStyle={{ background: 'transparent', padding: 0, margin: 0 }}
                        wrapLongLines
                      >
                        {promptText}
                      </SyntaxHighlighter>
                    </div>
                  ) : (
                    <span className="line-clamp-2 text-slate-300">{promptText}</span>
                  )}
                </TableCell>
                <TableCell className="text-xs text-slate-400">
                  {log.provider && log.model ? `${log.provider}/${log.model}` : '-'}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
};

const ResponsesTable: React.FC<{
  logs: LiveLogEntry[];
  expandedRows: Set<string>;
  toggleExpand: (id: string) => void;
}> = ({ logs, expandedRows, toggleExpand }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div ref={containerRef} className="h-full overflow-y-auto w-full">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[80px]">Time</TableHead>
            <TableHead className="w-[80px]">Iteration</TableHead>
            <TableHead className="w-[100px]">Role</TableHead>
            <TableHead>Response</TableHead>
            <TableHead className="w-[100px]">Latency</TableHead>
            <TableHead className="w-[80px]">Tokens</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {logs.map((log) => {
            const isExpanded = expandedRows.has(log.id);
            const responseText = log.metadata?.response || log.content;

            return (
              <TableRow
                key={log.id}
                className="cursor-pointer hover:bg-slate-800/50 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                onClick={() => toggleExpand(log.id)}
                onKeyPress={createKeyboardHandler(toggleExpand, log.id)}
                tabIndex={0}
              >
                <TableCell className="font-mono text-xs text-slate-500">
                  {formatTime(log.timestamp)}
                </TableCell>
                <TableCell className="text-center text-slate-400">
                  {extractIteration(log)}
                </TableCell>
                <TableCell>
                  {log.role && (
                    <Badge className={getRoleBadgeColor(log.role)}>
                      {log.role.toUpperCase()}
                    </Badge>
                  )}
                </TableCell>
                <TableCell className="font-mono text-sm">
                  {isExpanded ? (
                    <div>
                      <div className="flex justify-end">
                        {createCopyButton(responseText)}
                      </div>
                      <SyntaxHighlighter
                        language="text"
                        style={vscDarkPlus}
                        customStyle={{ background: 'transparent', padding: 0, margin: 0 }}
                        wrapLongLines
                      >
                        {responseText}
                      </SyntaxHighlighter>
                    </div>
                  ) : (
                    <span className="line-clamp-2 text-slate-300">{responseText}</span>
                  )}
                </TableCell>
                <TableCell className="text-xs text-slate-400">
                  {log.metadata?.latency_ms ? `${log.metadata.latency_ms.toFixed(0)}ms` : '-'}
                </TableCell>
                <TableCell className="text-xs text-green-400 text-center">
                  {log.metadata?.tokens || '-'}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
};

const JudgeTable: React.FC<{
  logs: LiveLogEntry[];
  expandedRows: Set<string>;
  toggleExpand: (id: string) => void;
}> = ({ logs, expandedRows, toggleExpand }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div ref={containerRef} className="h-full overflow-y-auto w-full">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[80px]">Time</TableHead>
            <TableHead className="w-[80px]">Iteration</TableHead>
            <TableHead className="w-[80px]">Score</TableHead>
            <TableHead>Reasoning</TableHead>
            <TableHead className="w-[80px]">Success</TableHead>
            <TableHead className="w-[100px]">Latency</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {logs.map((log) => {
            const isExpanded = expandedRows.has(log.id);
            const score = log.metadata?.score || 0;
            const reasoning = log.metadata?.reasoning || log.content;

            return (
              <React.Fragment key={log.id}>
                <TableRow
                  className="cursor-pointer hover:bg-slate-800/50 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  onClick={() => toggleExpand(log.id)}
                  onKeyPress={createKeyboardHandler(toggleExpand, log.id)}
                  tabIndex={0}
                >
                  <TableCell className="font-mono text-xs text-slate-500">
                    {formatTime(log.timestamp)}
                  </TableCell>
                  <TableCell className="text-center text-slate-400">
                    {extractIteration(log)}
                  </TableCell>
                  <TableCell>
                    <Badge className={getScoreColor(score)}>
                      {score.toFixed(2)}/10
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm">
                    {isExpanded ? (
                      <div>
                        <div className="flex justify-end mb-2">
                          {createCopyButton(reasoning + (log.metadata?.sub_scores ? '\n\nSub-scores:\n' + JSON.stringify(log.metadata.sub_scores, null, 2) : ''))}
                        </div>
                        <SyntaxHighlighter
                          language="text"
                          style={vscDarkPlus}
                          customStyle={{ background: 'transparent', padding: 0 }}
                        >
                          {reasoning}
                        </SyntaxHighlighter>
                      </div>
                    ) : (
                      <span className="line-clamp-2 text-slate-300">{reasoning}</span>
                    )}

                    {isExpanded && log.metadata?.sub_scores ? (
                      <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                        {Object.entries(log.metadata.sub_scores).map(([key, value]) => (
                          <div key={key} className="flex justify-between bg-slate-900 px-2 py-1 rounded">
                            <span className="text-slate-400">{key}:</span>
                            <span className="text-cyan-400">{String((value as number).toFixed(1))}</span>
                          </div>
                        ))}
                      </div>
                    ) : null}
                  </TableCell>
                  <TableCell className="text-center">
                    {log.metadata?.success ? 'SUCCESS' : 'BLOCKED'}
                  </TableCell>
                  <TableCell className="text-xs text-slate-400">
                    {log.metadata?.latency_ms ? `${log.metadata.latency_ms.toFixed(0)}ms` : '-'}
                  </TableCell>
                </TableRow>
              </React.Fragment>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
};

const TasksTable: React.FC<{
  tasks: TaskQueueItem[];
}> = ({ tasks }) => {
  return (
    <div className="max-h-[calc(100vh-200px)] overflow-y-auto min-h-[400px] w-full">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[80px]">Time</TableHead>
            <TableHead>Task Name</TableHead>
            <TableHead className="w-[100px]">Status</TableHead>
            <TableHead className="w-[120px]">Strategy</TableHead>
            <TableHead className="w-[80px]">Queue #</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {tasks.map((task) => {
            const statusConfig = getStatusBadge(task.status);

            return (
              <TableRow key={task.id}>
                <TableCell className="font-mono text-xs text-slate-500">
                  {task.startedAt ? formatTime(task.startedAt) : '-'}
                </TableCell>
                <TableCell className="text-slate-300">{task.name}</TableCell>
                <TableCell>
                  <Badge className={statusConfig.color}>
                    {task.status}
                  </Badge>
                </TableCell>
                <TableCell className="text-xs text-slate-400 font-mono">
                  {task.strategy || '-'}
                </TableCell>
                <TableCell className="text-center text-slate-400">
                  {task.queuePosition !== undefined ? `#${task.queuePosition}` : '-'}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
};

const CodeFlowTable: React.FC<{
  events: CodeFlowEvent[];
  expandedRows: Set<string>;
  toggleExpand: (id: string) => void;
}> = ({ events, expandedRows, toggleExpand }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [events]);

  return (
    <div ref={containerRef} className="h-full overflow-y-auto w-full">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[80px]">Time</TableHead>
            <TableHead className="w-[120px]">Event Type</TableHead>
            <TableHead>Description</TableHead>
            <TableHead className="w-[100px]">Details</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {events.map((event) => {
            const eventId = event.id || `${event.timestamp}-${event.event_type}`;
            const isExpanded = expandedRows.has(eventId);

            return (
              <React.Fragment key={eventId}>
                <TableRow
                  className="cursor-pointer hover:bg-slate-800/50"
                  onClick={() => toggleExpand(eventId)}
                >
                  <TableCell className="font-mono text-xs text-slate-500">
                    {formatTime(event.timestamp)}
                  </TableCell>
                  <TableCell>
                    <Badge className="bg-indigo-900/50 text-indigo-400">
                      {getEventIcon(event.event_type)} {event.event_type}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm text-slate-300">
                    {event.description || event.function_name || '-'}
                  </TableCell>
                  <TableCell className="text-center">
                    {(event.parameters || event.result) ? (
                      <span className="text-cyan-400 text-xs">
                        {isExpanded ? '▼' : '▶'} Expand
                      </span>
                    ) : null}
                  </TableCell>
                </TableRow>
                {isExpanded && (event.parameters || event.result) ? (
                  <TableRow>
                    <TableCell colSpan={4} className="bg-slate-900/50">
                      {event.parameters ? (
                        <div className="mb-2">
                          <div className="text-xs text-slate-400 mb-1">Parameters:</div>
                          <SyntaxHighlighter
                            language="json"
                            style={vscDarkPlus}
                            customStyle={{ fontSize: '11px' }}
                          >
                            {JSON.stringify(event.parameters, null, 2)}
                          </SyntaxHighlighter>
                        </div>
                      ) : null}
                      {event.result ? (
                        <div>
                          <div className="text-xs text-slate-400 mb-1">Result:</div>
                          <SyntaxHighlighter
                            language="json"
                            style={vscDarkPlus}
                            customStyle={{ fontSize: '11px' }}
                          >
                            {typeof event.result === 'string'
                              ? event.result
                              : JSON.stringify(event.result, null, 2)}
                          </SyntaxHighlighter>
                        </div>
                      ) : null}
                    </TableCell>
                  </TableRow>
                ) : null}
              </React.Fragment>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
};

const AllTable: React.FC<{
  logs: LiveLogEntry[];
  expandedRows: Set<string>;
  toggleExpand: (id: string) => void;
}> = ({ logs, expandedRows, toggleExpand }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div ref={containerRef} className="h-full overflow-y-auto w-full">
      <Table className="w-full">
        <TableHeader>
          <TableRow>
            <TableHead className="w-[80px]">Time</TableHead>
            <TableHead className="w-[80px]">Iteration</TableHead>
            <TableHead className="w-[100px]">Type</TableHead>
            <TableHead className="w-[100px]">Role</TableHead>
            <TableHead>Content</TableHead>
            <TableHead className="w-[150px]">Details</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {logs.map((log) => {
            const isExpanded = expandedRows.has(log.id);
            const roleColor = getRoleBadgeColor(log.role);
            const contentText = log.metadata?.response || log.metadata?.prompt || log.content;

            return (
              <TableRow
                key={log.id}
                className="cursor-pointer hover:bg-slate-800/50 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                onClick={() => toggleExpand(log.id)}
                onKeyPress={createKeyboardHandler(toggleExpand, log.id)}
                tabIndex={0}
              >
                <TableCell className="font-mono text-xs text-slate-500">
                  {formatTime(log.timestamp)}
                </TableCell>
                <TableCell className="text-center text-slate-400">
                  {extractIteration(log)}
                </TableCell>
                <TableCell>
                  <Badge className="bg-slate-700 text-slate-300">
                    {log.type}
                  </Badge>
                </TableCell>
                <TableCell>
                  {log.role && (
                    <Badge className={roleColor}>
                      {log.role.toUpperCase()}
                    </Badge>
                  )}
                </TableCell>
                <TableCell className="font-mono text-sm">
                  {isExpanded ? (
                    <div>
                      <div className="flex justify-end">
                        {createCopyButton(contentText)}
                      </div>
                      <SyntaxHighlighter
                        language="text"
                        style={vscDarkPlus}
                        customStyle={{ background: 'transparent', padding: 0, margin: 0 }}
                        wrapLongLines
                      >
                        {contentText}
                      </SyntaxHighlighter>
                    </div>
                  ) : (
                    <span className="line-clamp-2 text-slate-300">{contentText}</span>
                  )}
                </TableCell>
                <TableCell className="text-xs text-slate-400">
                  {log.metadata?.latency_ms ? `${log.metadata.latency_ms.toFixed(0)}ms` : '-'}
                  {log.metadata?.tokens ? ` / ${log.metadata.tokens} tokens` : ''}
                  {log.provider && log.model ? ` / ${log.provider}/${log.model}` : ''}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
};

const VulnerabilitiesTable: React.FC<{
  logs: LiveLogEntry[];
  expandedRows: Set<string>;
  toggleExpand: (id: string) => void;
}> = ({ logs }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div ref={containerRef} className="h-full overflow-y-auto w-full">
      <Table className="w-full">
        <TableHeader>
          <TableRow>
            <TableHead className="w-[80px]">Time</TableHead>
            <TableHead className="w-[80px]">Iteration</TableHead>
            <TableHead className="w-[120px]">Severity</TableHead>
            <TableHead>Vulnerability</TableHead>
            <TableHead className="w-[100px]">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {logs.map((log) => {
            const vulnerabilityId = log.metadata?.vulnerability_id;
            const severity = (log.metadata?.severity as string) || 'unknown';

            return (
              <TableRow
                key={log.id}
                className="hover:bg-amber-900/20 focus:outline-none focus:ring-2 focus:ring-cyan-500"
              >
                <TableCell className="font-mono text-xs text-slate-500">
                  {formatTime(log.timestamp)}
                </TableCell>
                <TableCell className="text-center text-slate-400">
                  {extractIteration(log)}
                </TableCell>
                <TableCell>
                  <Badge className="bg-amber-900/50 text-amber-400 border-amber-700">
                    {severity.toUpperCase()}
                  </Badge>
                </TableCell>
                <TableCell className="text-sm text-amber-300">
                  <Link
                    to={`/vulnerabilities/${vulnerabilityId}`}
                    className="text-amber-400 hover:text-amber-300 hover:underline font-semibold"
                  >
                    {log.content} → View Details
                  </Link>
                </TableCell>
                <TableCell className="text-center">
                  <Link
                    to={`/vulnerabilities/${vulnerabilityId}`}
                    className="text-cyan-400 hover:text-cyan-300 text-xs"
                  >
                    Details
                  </Link>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
};

const ErrorsTable: React.FC<{
  logs: LiveLogEntry[];
  expandedRows: Set<string>;
  toggleExpand: (id: string) => void;
}> = ({ logs, expandedRows, toggleExpand }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div ref={containerRef} className="h-full overflow-y-auto w-full">
      <Table className="w-full">
        <TableHeader>
          <TableRow>
            <TableHead className="w-[80px]">Time</TableHead>
            <TableHead className="w-[120px]">Error Type</TableHead>
            <TableHead>Message</TableHead>
            <TableHead className="w-[100px]">Context</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {logs.map((log) => {
            const isExpanded = expandedRows.has(log.id);
            const isVulnerability = log.metadata?.vulnerability_id;
            const vulnerabilityId = log.metadata?.vulnerability_id;

            return (
              <React.Fragment key={log.id}>
                <TableRow
                  className={`${isVulnerability ? 'hover:bg-amber-900/20' : 'hover:bg-slate-800/50'} focus:outline-none focus:ring-2 focus:ring-cyan-500`}
                  onClick={() => !isVulnerability && toggleExpand(log.id)}
                  onKeyPress={(e) => !isVulnerability && createKeyboardHandler(toggleExpand, log.id)(e)}
                  tabIndex={0}
                >
                  <TableCell className="font-mono text-xs text-slate-500">
                    {formatTime(log.timestamp)}
                  </TableCell>
                  <TableCell>
                    <Badge className={isVulnerability ? "bg-amber-900/50 text-amber-400 border-amber-700" : "bg-red-900/50 text-red-400 border-red-700"}>
                      {isVulnerability ? 'VULN' : 'ERROR'} {log.type}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm text-red-300">
                    {isVulnerability ? (
                      <Link
                        to={`/vulnerabilities/${vulnerabilityId}`}
                        className="text-amber-400 hover:text-amber-300 hover:underline font-semibold"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {log.content} → View Details
                      </Link>
                    ) : (
                      log.content
                    )}
                  </TableCell>
                  <TableCell className="text-center">
                    {isVulnerability ? (
                      <Link
                        to={`/vulnerabilities/${vulnerabilityId}`}
                        className="text-cyan-400 hover:text-cyan-300 text-xs"
                        onClick={(e) => e.stopPropagation()}
                      >
                        Details
                      </Link>
                    ) : log.metadata ? (
                      <span className="text-cyan-400 text-xs">{isExpanded ? '▼' : '▶'}</span>
                    ) : null}
                  </TableCell>
                </TableRow>
                {isExpanded && log.metadata && !isVulnerability ? (
                  <TableRow>
                    <TableCell colSpan={4} className="bg-slate-900/50">
                      <div className="flex justify-end mb-2">
                        {createCopyButton(JSON.stringify(log.metadata, null, 2))}
                      </div>
                      <pre className="text-xs text-slate-400 overflow-x-auto">
                        {JSON.stringify(log.metadata, null, 2)}
                      </pre>
                    </TableCell>
                  </TableRow>
                ) : null}
              </React.Fragment>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
};

// Export Functions
const convertToCSV = (data: unknown[]): string => {
  if (data.length === 0) return '';

  const headers = Object.keys(data[0] as Record<string, unknown>);
  const rows = data.map((item) =>
    headers
      .map((header) => {
        const value = (item as Record<string, unknown>)[header];
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      })
      .join(',')
  );

  return [headers.join(','), ...rows].join('\n');
};

const downloadBlob = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

// Main Component
export const LiveLogPanel: React.FC<LiveLogPanelProps> = ({
  logs,
  tasks = [],
  codeFlowEvents = [],
  onExport,
}) => {
  const [activeTab, setActiveTab] = useState<'all' | 'requests' | 'responses' | 'judge' | 'tasks' | 'codeflow' | 'errors' | 'vulnerabilities'>('all');
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  // Filter logs by type (show ALL logs, no limit - complete history)
  const requestLogs = logs.filter((log) => log.type === 'llm_request');
  const responseLogs = logs.filter((log) => log.type === 'llm_response');
  const judgeLogs = logs.filter((log) => log.type === 'judge');
  const errorLogs = logs.filter((log) => (log.type === 'error' || log.type === 'llm_error') && !log.metadata?.vulnerability_id);
  const allLogs = logs;  // Show ALL logs
  // Vulnerabilities: comprehensive filter for all vulnerability-related logs
  const vulnerabilityLogs = logs.filter((log) => {
    // Condition 1: Has vulnerability_id in metadata
    if (log.metadata?.vulnerability_id) return true;
    
    // Condition 2: Content contains 'VULNERABILITY FOUND' (case-insensitive)
    if (typeof log.content === 'string' && 
        log.content.toUpperCase().includes('VULNERABILITY FOUND')) return true;
    
    // Condition 3: Type is 'error' AND has severity in metadata (vulnerability marker)
    if (log.type === 'error' && log.metadata?.severity) return true;
    
    // Condition 4: Metadata has vulnerability-specific fields (successful_prompt + high score)
    if (log.metadata?.successful_prompt && 
        log.metadata?.judge_score && 
        (log.metadata.judge_score as number) >= 7.0) return true;
    
    return false;
  });
  
  // Debug: Log vulnerability filter results
  useEffect(() => {
    console.log(`[LiveLogPanel] Vulnerability Filter: ${vulnerabilityLogs.length} found from ${logs.length} total logs`);
    if (vulnerabilityLogs.length > 0) {
      console.log('[LiveLogPanel] Sample vulnerability log:', vulnerabilityLogs[0]);
    }
  }, [logs.length, vulnerabilityLogs.length]);

  const tabCounts = {
    all: allLogs.length,
    requests: requestLogs.length,
    responses: responseLogs.length,
    judge: judgeLogs.length,
    tasks: tasks.length,
    codeflow: codeFlowEvents.length,
    errors: errorLogs.length,
    vulnerabilities: vulnerabilityLogs.length,
  };

  const toggleExpand = (id: string) => {
    setExpandedRows((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        // Limit to max 50 expanded rows for performance
        const MAX_EXPANDED = 50;
        if (newSet.size >= MAX_EXPANDED) {
          // Remove oldest expanded row
          const firstId = Array.from(newSet)[0];
          newSet.delete(firstId);
        }
        newSet.add(id);
      }
      return newSet;
    });
  };

  const toggleExpandAll = () => {
    setExpandedRows((prev) => {
      if (prev.size > 0) {
        // Collapse all
        return new Set();
      } else {
        // Expand all visible logs in current tab
        let allIds: string[] = [];
        switch (activeTab) {
          case 'requests':
            allIds = requestLogs.map(log => log.id);
            break;
          case 'responses':
            allIds = responseLogs.map(log => log.id);
            break;
          case 'judge':
            allIds = judgeLogs.map(log => log.id);
            break;
          case 'codeflow':
            allIds = codeFlowEvents.map(event => event.id || `${event.timestamp}-${event.event_type}`);
            break;
          case 'errors':
            allIds = errorLogs.map(log => log.id);
            break;
        }
        return new Set(allIds.slice(0, 50)); // Limit to 50 for performance
      }
    });
  };


  const exportLogs = (format: 'json' | 'csv') => {
    let dataToExport: unknown[] = [];

    switch (activeTab) {
      case 'all':
        dataToExport = allLogs;
        break;
      case 'requests':
        dataToExport = requestLogs;
        break;
      case 'responses':
        dataToExport = responseLogs;
        break;
      case 'judge':
        dataToExport = judgeLogs;
        break;
      case 'tasks':
        dataToExport = tasks;
        break;
      case 'codeflow':
        dataToExport = codeFlowEvents;
        break;
      case 'errors':
        dataToExport = errorLogs;
        break;
      case 'vulnerabilities':
        dataToExport = vulnerabilityLogs;
        break;
    }

    if (onExport) {
      onExport(dataToExport, format);
    } else {
      if (format === 'json') {
        const blob = new Blob([JSON.stringify(dataToExport, null, 2)], { type: 'application/json' });
        downloadBlob(blob, `logs-${activeTab}-${Date.now()}.json`);
      } else if (format === 'csv') {
        const csv = convertToCSV(dataToExport);
        const blob = new Blob([csv], { type: 'text/csv' });
        downloadBlob(blob, `logs-${activeTab}-${Date.now()}.csv`);
      }
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-950 rounded-lg border border-slate-800 overflow-hidden">
      {/* Header with Export */}
      <div className="flex items-center justify-between px-4 py-2 bg-slate-900/80 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <span className="text-lg">📜</span>
          <h3 className="font-semibold text-slate-200">Live Logs</h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={toggleExpandAll}
            className="px-2 py-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 rounded transition-colors"
            title={expandedRows.size > 0 ? 'Collapse All' : 'Expand All'}
          >
            {expandedRows.size > 0 ? '📥 Collapse All' : '📤 Expand All'}
          </button>
          <button
            onClick={() => exportLogs('json')}
            className="px-2 py-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 rounded transition-colors"
          >
            JSON
          </button>
          <button
            onClick={() => exportLogs('csv')}
            className="px-2 py-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 rounded transition-colors"
          >
            CSV
          </button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as typeof activeTab)} className="flex-1 flex flex-col">
        <TabsList className="bg-slate-900 border-b border-slate-800 rounded-none justify-start">
          <TabsTrigger value="all">
            All <Badge className="ml-1">{String(tabCounts.all)}</Badge>
          </TabsTrigger>
          <TabsTrigger value="requests">
            Requests <Badge className="ml-1">{String(tabCounts.requests)}</Badge>
          </TabsTrigger>
          <TabsTrigger value="responses">
            Responses <Badge className="ml-1">{String(tabCounts.responses)}</Badge>
          </TabsTrigger>
          <TabsTrigger value="judge">
            Judge <Badge className="ml-1">{String(tabCounts.judge)}</Badge>
          </TabsTrigger>
          <TabsTrigger value="tasks">
            Tasks <Badge className="ml-1">{String(tabCounts.tasks)}</Badge>
          </TabsTrigger>
          <TabsTrigger value="codeflow">
            Code Flow <Badge className="ml-1">{String(tabCounts.codeflow)}</Badge>
          </TabsTrigger>
          <TabsTrigger value="errors">
            Errors <Badge className="ml-1">{String(tabCounts.errors)}</Badge>
          </TabsTrigger>
          <TabsTrigger value="vulnerabilities">
            Vulnerabilities <Badge className="ml-1">{String(tabCounts.vulnerabilities)}</Badge>
          </TabsTrigger>
        </TabsList>

        <div className="flex-1 overflow-hidden flex flex-col min-h-0">
          <TabsContent value="all" className="flex-1 m-0 flex flex-col min-h-0">
            <AllTable logs={allLogs} expandedRows={expandedRows} toggleExpand={toggleExpand} />
          </TabsContent>

          <TabsContent value="requests" className="flex-1 m-0 flex flex-col min-h-0">
            <RequestsTable logs={requestLogs} expandedRows={expandedRows} toggleExpand={toggleExpand} />
          </TabsContent>

          <TabsContent value="responses" className="flex-1 m-0 flex flex-col min-h-0">
            <ResponsesTable logs={responseLogs} expandedRows={expandedRows} toggleExpand={toggleExpand} />
          </TabsContent>

          <TabsContent value="judge" className="flex-1 m-0 flex flex-col min-h-0">
            <JudgeTable logs={judgeLogs} expandedRows={expandedRows} toggleExpand={toggleExpand} />
          </TabsContent>

          <TabsContent value="tasks" className="flex-1 m-0 flex flex-col min-h-0">
            <TasksTable tasks={tasks} />
          </TabsContent>

          <TabsContent value="codeflow" className="flex-1 m-0 flex flex-col min-h-0">
            <CodeFlowTable events={codeFlowEvents} expandedRows={expandedRows} toggleExpand={toggleExpand} />
          </TabsContent>

          <TabsContent value="errors" className="flex-1 m-0 flex flex-col min-h-0">
            <ErrorsTable logs={errorLogs} expandedRows={expandedRows} toggleExpand={toggleExpand} />
          </TabsContent>

          <TabsContent value="vulnerabilities" className="flex-1 m-0 flex flex-col min-h-0">
            <VulnerabilitiesTable logs={vulnerabilityLogs} expandedRows={expandedRows} toggleExpand={toggleExpand} />
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
};

export default LiveLogPanel;
