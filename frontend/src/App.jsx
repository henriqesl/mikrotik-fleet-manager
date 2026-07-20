import {
  Activity,
  Bell,
  ChevronRight,
  CircleAlert,
  Gauge,
  LayoutDashboard,
  LoaderCircle,
  Plus,
  RefreshCw,
  Router,
  Search,
  Server,
  Settings,
  ShieldCheck,
  Wifi,
  WifiOff,
} from "lucide-react";
import { useMemo, useState } from "react";

import { RouterDetailDrawer } from "./components/RouterDetailDrawer";
import { RouterRegistrationModal } from "./components/RouterRegistrationModal";
import { useFleetDashboard } from "./hooks/useFleetDashboard";


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


const statusStyles = {
  online: {
    label: "Online",
    badge:
      "border-emerald-400/20 bg-emerald-400/10 text-emerald-300",
    dot: "bg-emerald-400",
  },
  offline: {
    label: "Offline",
    badge:
      "border-red-400/20 bg-red-400/10 text-red-300",
    dot: "bg-red-400",
  },
  error: {
    label: "Error",
    badge:
      "border-amber-400/20 bg-amber-400/10 text-amber-300",
    dot: "bg-amber-400",
  },
  unknown: {
    label: "Unknown",
    badge:
      "border-slate-400/20 bg-slate-400/10 text-slate-300",
    dot: "bg-slate-400",
  },
};


function getRouterStatus(router) {
  return String(
    router.status
      ?? router.current_status
      ?? "unknown",
  ).toLowerCase();
}


function getCpuUsage(router) {
  const value =
    router.cpu_usage_percent
    ?? router.cpu_usage
    ?? null;

  const numericValue = Number(value);

  return Number.isFinite(numericValue)
    ? numericValue
    : null;
}


function getMemoryUsage(router) {
  const value =
    router.memory_usage_percent
    ?? router.memory_usage
    ?? null;

  const numericValue = Number(value);

  return Number.isFinite(numericValue)
    ? numericValue
    : null;
}


function formatPercentage(value) {
  return value === null
    ? "—"
    : `${Math.round(value)}%`;
}


function formatUptime(seconds) {
  const numericSeconds = Number(seconds);

  if (
    !Number.isFinite(numericSeconds)
    || numericSeconds < 0
  ) {
    return "—";
  }

  const days = Math.floor(
    numericSeconds / 86_400,
  );

  const hours = Math.floor(
    (numericSeconds % 86_400) / 3_600,
  );

  const minutes = Math.floor(
    (numericSeconds % 3_600) / 60,
  );

  if (days > 0) {
    return `${days}d ${hours}h`;
  }

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }

  return `${minutes}m`;
}


function formatDateTime(value) {
  if (!value) {
    return "Never";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return new Intl.DateTimeFormat(
    "pt-BR",
    {
      dateStyle: "short",
      timeStyle: "short",
    },
  ).format(date);
}


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


function StatusBadge({ status }) {
  const style =
    statusStyles[status]
    ?? statusStyles.unknown;

  return (
    <span
      className={[
        "inline-flex items-center gap-2 rounded-full border px-2.5 py-1",
        "text-xs font-medium",
        style.badge,
      ].join(" ")}
    >
      <span
        className={[
          "size-1.5 rounded-full",
          style.dot,
        ].join(" ")}
      />

      {style.label}
    </span>
  );
}


function LoadingTable() {
  return (
    <div className="grid min-h-80 place-items-center p-8">
      <div className="text-center">
        <LoaderCircle className="mx-auto size-7 animate-spin text-emerald-400" />

        <p className="mt-3 text-sm text-slate-500">
          Loading router fleet...
        </p>
      </div>
    </div>
  );
}


function EmptyRouterTable({
  hasSearch,
  onAddRouter,
}) {
  return (
    <div className="grid min-h-80 place-items-center p-8 text-center">
      <div className="max-w-sm">
        <div className="mx-auto flex size-14 items-center justify-center rounded-2xl border border-white/[0.07] bg-white/[0.03]">
          {hasSearch ? (
            <Search className="size-6 text-slate-500" />
          ) : (
            <Router className="size-6 text-slate-500" />
          )}
        </div>

        <h3 className="mt-5 font-semibold text-slate-200">
          {hasSearch
            ? "No matching routers"
            : "No routers registered"}
        </h3>

        <p className="mt-2 text-sm leading-6 text-slate-500">
          {hasSearch
            ? "Try searching by another name, IP address, model or identity."
            : "Add your first MikroTik router to begin monitoring connectivity, CPU, memory and uptime."}
        </p>

        {!hasSearch && (
          <button
            type="button"
            onClick={onAddRouter}
            className="mx-auto mt-5 flex items-center gap-1 text-sm font-medium text-emerald-400 transition hover:text-emerald-300"
          >
            Register a router
            <ChevronRight className="size-4" />
          </button>
        )}
      </div>
    </div>
  );
}


function RouterTable({
  routers,
  isLoading,
  search,
  setSearch,
  onAddRouter,
  onSelectRouter,
}) {
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
              value={search}
              onChange={(event) => {
                setSearch(event.target.value);
              }}
              placeholder="Search by name or IP"
              className="h-10 w-full rounded-xl border border-white/10 bg-slate-950/70 pl-10 pr-4 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-emerald-400/40 sm:w-64"
            />
          </label>

          <button
            type="button"
            onClick={onAddRouter}
            className="flex h-10 items-center justify-center gap-2 rounded-xl bg-emerald-400 px-4 text-sm font-semibold text-slate-950 transition hover:bg-emerald-300"
          >
            <Plus className="size-4" />
            Add Router
          </button>
        </div>
      </div>

      {isLoading ? (
        <LoadingTable />
      ) : routers.length === 0 ? (
        <EmptyRouterTable
          hasSearch={search.trim().length > 0}
          onAddRouter={onAddRouter}
        />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1000px] text-left">
            <thead className="border-b border-white/[0.06] bg-slate-950/30">
              <tr className="text-xs uppercase tracking-wider text-slate-500">
                <th className="px-5 py-3 font-medium">
                  Router
                </th>

                <th className="px-5 py-3 font-medium">
                  Status
                </th>

                <th className="px-5 py-3 font-medium">
                  Model
                </th>

                <th className="px-5 py-3 font-medium">
                  CPU
                </th>

                <th className="px-5 py-3 font-medium">
                  Memory
                </th>

                <th className="px-5 py-3 font-medium">
                  Uptime
                </th>

                <th className="px-5 py-3 font-medium">
                  Last check
                </th>
              </tr>
            </thead>

            <tbody className="divide-y divide-white/[0.05]">
              {routers.map((routerItem) => {
                const status =
                  getRouterStatus(routerItem);

                const cpuUsage =
                  getCpuUsage(routerItem);

                const memoryUsage =
                  getMemoryUsage(routerItem);

                return (
                  <tr
                    key={routerItem.id}
                    role="button"
                    tabIndex={0}
                    aria-label={`Open details for ${routerItem.name}`}
                    onClick={() => {
                      onSelectRouter(routerItem.id);
                    }}
                    onKeyDown={(event) => {
                      if (
                        event.key === "Enter"
                        || event.key === " "
                      ) {
                        event.preventDefault();

                        onSelectRouter(
                          routerItem.id,
                        );
                      }
                    }}
                    className="cursor-pointer transition hover:bg-white/[0.04] focus:bg-white/[0.04] focus:outline-none"
                  >
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        <div className="flex size-9 shrink-0 items-center justify-center rounded-xl border border-white/[0.07] bg-white/[0.03]">
                          <Router className="size-4 text-slate-400" />
                        </div>

                        <div>
                          <p className="text-sm font-medium text-slate-200">
                            {routerItem.name}
                          </p>

                          <p className="mt-0.5 text-xs text-slate-500">
                            {routerItem.management_ip}
                          </p>
                        </div>
                      </div>
                    </td>

                    <td className="px-5 py-4">
                      <StatusBadge status={status} />
                    </td>

                    <td className="px-5 py-4">
                      <p className="text-sm text-slate-300">
                        {routerItem.model ?? "—"}
                      </p>

                      <p className="mt-0.5 text-xs text-slate-600">
                        {routerItem.routeros_version
                          ?? routerItem.identity
                          ?? "No device data"}
                      </p>
                    </td>

                    <td className="px-5 py-4 text-sm text-slate-300">
                      {formatPercentage(cpuUsage)}
                    </td>

                    <td className="px-5 py-4 text-sm text-slate-300">
                      {formatPercentage(memoryUsage)}
                    </td>

                    <td className="px-5 py-4 text-sm text-slate-300">
                      {formatUptime(
                        routerItem.uptime_seconds,
                      )}
                    </td>

                    <td className="px-5 py-4 text-sm text-slate-400">
                      {formatDateTime(
                        routerItem.last_checked_at,
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}


function App() {
  const [search, setSearch] = useState("");

  const [
    isRegistrationOpen,
    setIsRegistrationOpen,
  ] = useState(false);

  const [
    selectedRouterId,
    setSelectedRouterId,
  ] = useState(null);

  const {
    routers,
    monitoringStatus,
    statistics,
    isLoading,
    isRefreshing,
    error,
    lastUpdatedAt,
    refresh,
  } = useFleetDashboard();

  const filteredRouters = useMemo(() => {
    const normalizedSearch =
      search.trim().toLowerCase();

    if (!normalizedSearch) {
      return routers;
    }

    return routers.filter((routerItem) => {
      const searchableValues = [
        routerItem.name,
        routerItem.management_ip,
        routerItem.public_ip,
        routerItem.model,
        routerItem.identity,
      ];

      return searchableValues.some(
        (value) =>
          String(value ?? "")
            .toLowerCase()
            .includes(normalizedSearch),
      );
    });
  }, [routers, search]);

  const statisticCards = [
    {
      label: "Total Routers",
      value: statistics.total,
      description: "Registered active devices",
      icon: Server,
    },
    {
      label: "Online",
      value: statistics.online,
      description: "Reachable devices",
      icon: Wifi,
    },
    {
      label: "Offline",
      value: statistics.offline,
      description: "Unavailable devices",
      icon: WifiOff,
    },
    {
      label: "CPU Alerts",
      value: statistics.cpuAlerts,
      description: "Usage at or above 80%",
      icon: CircleAlert,
    },
  ];

  return (
    <div className="min-h-screen lg:flex">
      <Sidebar />

      <div className="min-w-0 flex-1">
        <Header />

        <main className="px-5 py-6 md:px-8 md:py-8">
          <div className="mx-auto max-w-7xl">
            <div className="mb-6 flex flex-col gap-3 rounded-xl border border-emerald-400/10 bg-emerald-400/5 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-2 text-sm text-emerald-200">
                <Gauge className="size-4 shrink-0" />

                <span>
                  Polling worker:{" "}
                  <strong>
                    {monitoringStatus?.worker_running
                      ? "running"
                      : "stopped"}
                  </strong>
                </span>

                {monitoringStatus?.cycle_in_progress && (
                  <span className="text-emerald-400">
                    · cycle in progress
                  </span>
                )}
              </div>

              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-500">
                  {lastUpdatedAt
                    ? `Updated ${lastUpdatedAt.toLocaleTimeString("pt-BR")}`
                    : "Waiting for data"}
                </span>

                <button
                  type="button"
                  disabled={isRefreshing}
                  onClick={() => {
                    refresh();
                  }}
                  className="flex items-center gap-2 rounded-lg border border-white/10 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:border-white/20 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <RefreshCw
                    className={[
                      "size-3.5",
                      isRefreshing
                        ? "animate-spin"
                        : "",
                    ].join(" ")}
                  />

                  Refresh
                </button>
              </div>
            </div>

            {error && (
              <div className="mb-6 flex items-start gap-3 rounded-xl border border-red-400/20 bg-red-400/10 px-4 py-3">
                <CircleAlert className="mt-0.5 size-4 shrink-0 text-red-300" />

                <div>
                  <p className="text-sm font-medium text-red-200">
                    Unable to update all dashboard data
                  </p>

                  <p className="mt-1 text-xs leading-5 text-red-300/70">
                    {error}
                  </p>
                </div>
              </div>
            )}

            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {statisticCards.map((statistic) => (
                <StatisticCard
                  key={statistic.label}
                  {...statistic}
                />
              ))}
            </section>

            <div className="mt-6">
              <RouterTable
                routers={filteredRouters}
                isLoading={isLoading}
                search={search}
                setSearch={setSearch}
                onAddRouter={() => {
                  setIsRegistrationOpen(true);
                }}
                onSelectRouter={(routerId) => {
                  setSelectedRouterId(routerId);
                }}
              />
            </div>
          </div>
        </main>
      </div>

      <RouterRegistrationModal
        isOpen={isRegistrationOpen}
        onClose={() => {
          setIsRegistrationOpen(false);
        }}
        onCreated={() => {
          refresh({
            silent: true,
          });
        }}
      />

      <RouterDetailDrawer
        isOpen={selectedRouterId !== null}
        routerId={selectedRouterId}
        onClose={() => {
          setSelectedRouterId(null);
        }}
        onChanged={() => {
          refresh({
            silent: true,
          });
        }}
      />
    </div>
  );
}


export default App;