import { Outlet, NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  MessageSquare,
  Zap,
  CalendarCheck,
  Wand2,
  Activity,
} from 'lucide-react'

const NAV = [
  { to: '/dashboard', label: 'Dashboard',  Icon: LayoutDashboard },
  { to: '/chat',      label: 'Chat',        Icon: MessageSquare },
  { to: '/triggers',  label: 'Triggers',    Icon: Zap },
  { to: '/bookings',  label: 'Bookings',    Icon: CalendarCheck },
  { to: '/generate',  label: 'Generator',   Icon: Wand2 },
]

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-56 flex-shrink-0 flex flex-col bg-surface-800 border-r border-surface-700">
        {/* Logo */}
        <div className="flex items-center gap-2 px-4 py-5 border-b border-surface-700">
          <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center">
            <Activity size={16} className="text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-white leading-tight">SalesPulse</p>
            <p className="text-[10px] text-brand-400 font-medium uppercase tracking-widest">AI</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1">
          {NAV.map(({ to, label, Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ` +
                (isActive
                  ? 'bg-brand-600 text-white'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-surface-700')
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-surface-700">
          <p className="text-xs text-slate-500 text-center">v1.0.0</p>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <Outlet />
      </main>
    </div>
  )
}