import {
  Activity,
  Bell,
  ChevronRight,
  CircleAlert,
  Gauge,
  LayoutDashboard,
  Plus,
  Router,
  Search,
  Server,
  Settings,
  ShieldCheck,
  Wifi,
  WifiOff,
} from "lucide-react";

const navigationItems = [
  {
    label: "Dashboard",
    icon: LayoutDashboard,
    active: true,
  },
  {
    label: "Routers",
    icon: Router,
    active: false,
  },
  {
    label: "Monitoring",
    icon: Activity,
    active: false,
  },
  {
    label: "Settings",
    icon: Settings,
    active: false,
  },
];

const statistics = [
  {
    label: "Total Routers",
    value: "0",
    description: "Registered devices",
    icon: Server,
  },
  {
    label: "Online",
    value: "0",
    description: "Reachable devices",
    icon: Wifi,
  },
  {
    label: "Offline",
    value: "0",
    description: "Unavailable devices",
    icon: WifiOff,
  },
  {
    label: "CPU Alerts",
    value: "0",
    description: "Usage above 80%",
    icon: CircleAlert,
  },
];

function Brand() {
  return (
    <div className="flex items-center gap-3">
      <div className="flex size-10 items-center justify-center rounded-xl border border-emerald-400/20 bg-emerald-400/10">
        <ShieldCheck
          className="size-5 text-emerald-400"
          strokeWidth={2}
        />
      </div>

      <div>
        <p className="text-sm font-semibold tracking-[0.22em] text-white">
          ARGOS
        </p>

        <p className="text-xs text-slate-500">
          MikroTik Fleet Manager
        </p>
      </div>
    </div>
  );
}

function Sidebar() {
  return (
    <aside className="hidden min-h-screen w-64 shrink-0 border-r border-white/5 bg-slate-950/70 px-4 py-5 backdrop-blur-xl lg:flex lg:flex-col">
      <div className="px-2">
        <Brand />
      </div>

      <nav className="mt-10 space-y-1">
        {navigationItems.map((item) => {
          const Icon = item.icon;

          return (
            <button
              key={item.label}
              type="button"
              className={[
                "flex w-full items-center gap-3 rounded-xl px-3 py-2.5",
                "text-sm font-medium transition",
                item.active
                  ? "bg-emerald-400/10 text-emerald-300"
                  : "text-slate-400 hover:bg-white/5 hover:text-slate-100",
              ].join(" ")}
            >
              <Icon className="size-4" />

              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="mt-auto rounded-2xl border border-emerald-400/10 bg-emerald-400/5 p-4">
        <div className="flex items-center gap-2 text-emerald-300">
          <ShieldCheck className="size-4" />

          <span className="text-xs font-semibold uppercase tracking-wider">
            Secure network
          </span>
        </div>

        <p className="mt-2 text-xs leading-5 text-slate-500">
          Router communication is restricted to the configured
          WireGuard management network.
        </p>
      </div>
    </aside>
  );
}

function Header() {
  return (
    <header className="flex min-h-20 items-center justify-between border-b border-white/5 px-5 md:px-8">
      <div>
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-emerald-400">
          Network operations
        </p>

        <h1 className="mt-1 text-xl font-semibold text-white">
          Fleet Dashboard
        </h1>
      </div>

      <div className="flex items-center gap-3">
        <button
          type="button"
          aria-label="Notifications"
          className="flex size-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] text-slate-400 transition hover:border-white/20 hover:text-white"
        >
          <Bell className="size-4" />
        </button>

        <div className="hidden items-center gap-3 border-l border-white/10 pl-4 sm:flex">
          <div className="flex size-9 items-center justify-center rounded-full bg-emerald-400/10 text-sm font-semibold text-emerald-300">
            HS
          </div>

          <div>
            <p className="text-sm font-medium text-slate-200">
              Administrator
            </p>

            <p className="text-xs text-slate-500">
              ARGOS Operator
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}

function StatisticCard({
  label,
  value,
  description,
  icon: Icon,
}) {
  return (
    <article className="rounded-2xl border border-white/[0.07] bg-slate-900/50 p-5 shadow-2xl shadow-black/10">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-400">
            {label}
          </p>

          <p className="mt-3 text-3xl font-semibold tracking-tight text-white">
            {value}
          </p>
        </div>

        <div className="flex size-10 items-center justify-center rounded-xl border border-white/[0.07] bg-white/[0.03] text-slate-300">
          <Icon className="size-5" />
        </div>
      </div>

      <p className="mt-4 text-xs text-slate-500">
        {description}
      </p>
    </article>
  );
}

function EmptyRouterTable() {
  return (
    <section className="overflow-hidden rounded-2xl border border-white/[0.07] bg-slate-900/40">
      <div className="flex flex-col gap-4 border-b border-white/[0.06] p-5 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="font-semibold text-white">
            Managed Routers
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Monitor and manage your RouterOS devices.
          </p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row">
          <label className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-500" />

            <input
              type="search"
              placeholder="Search by name or IP"
              className="h-10 w-full rounded-xl border border-white/10 bg-slate-950/70 pl-10 pr-4 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-emerald-400/40 sm:w-64"
            />
          </label>

          <button
            type="button"
            className="flex h-10 items-center justify-center gap-2 rounded-xl bg-emerald-400 px-4 text-sm font-semibold text-slate-950 transition hover:bg-emerald-300"
          >
            <Plus className="size-4" />
            Add Router
          </button>
        </div>
      </div>

      <div className="grid min-h-80 place-items-center p-8 text-center">
        <div className="max-w-sm">
          <div className="mx-auto flex size-14 items-center justify-center rounded-2xl border border-white/[0.07] bg-white/[0.03]">
            <Router className="size-6 text-slate-500" />
          </div>

          <h3 className="mt-5 font-semibold text-slate-200">
            No routers registered
          </h3>

          <p className="mt-2 text-sm leading-6 text-slate-500">
            Add your first MikroTik router to begin monitoring
            connectivity, CPU, memory and uptime.
          </p>

          <button
            type="button"
            className="mx-auto mt-5 flex items-center gap-1 text-sm font-medium text-emerald-400 transition hover:text-emerald-300"
          >
            Register a router
            <ChevronRight className="size-4" />
          </button>
        </div>
      </div>
    </section>
  );
}

function App() {
  return (
    <div className="min-h-screen lg:flex">
      <Sidebar />

      <div className="min-w-0 flex-1">
        <Header />

        <main className="px-5 py-6 md:px-8 md:py-8">
          <div className="mx-auto max-w-7xl">
            <div className="mb-6 flex items-center gap-2 rounded-xl border border-emerald-400/10 bg-emerald-400/5 px-4 py-3 text-sm text-emerald-200">
              <Gauge className="size-4 shrink-0" />

              <span>
                ARGOS frontend foundation is operational.
              </span>
            </div>

            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {statistics.map((statistic) => (
                <StatisticCard
                  key={statistic.label}
                  {...statistic}
                />
              ))}
            </section>

            <div className="mt-6">
              <EmptyRouterTable />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;