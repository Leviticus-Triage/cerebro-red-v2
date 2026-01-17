/**
 * Sidebar navigation component.
 */

import { NavLink } from 'react-router-dom';
import {
  Home,
  FlaskConical,
  AlertTriangle,
  BarChart3,
  FileText,
  Shield,
  Settings,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { to: '/', icon: Home, label: 'Dashboard' },
  { to: '/experiments', icon: FlaskConical, label: 'Experiments' },
  { to: '/templates', icon: FileText, label: 'Templates' },
  { to: '/jailbreak-templates', icon: Shield, label: 'Jailbreak Templates' },
  { to: '/vulnerabilities', icon: AlertTriangle, label: 'Vulnerabilities' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export function Sidebar() {
  return (
    <aside className="w-64 border-r bg-background">
      <nav className="space-y-1 p-4">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-accent hover:text-accent-foreground'
              )
            }
          >
            <item.icon className="h-5 w-5" />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
