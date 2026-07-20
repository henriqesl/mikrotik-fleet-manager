import {
  AlertTriangle,
  Box,
  CalendarClock,
  Cpu,
  Globe2,
  HardDrive,
  LoaderCircle,
  Network,
  RefreshCw,
  Router,
  ShieldCheck,
  TimerReset,
  X,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useState,
} from "react";

import { routerService } from "../services/routerService";


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
    router?.status
      ?? router?.current_status
      ?? "unknown",
  ).toLowerCase();
}


function getPercentage(router, ...fields) {
  for (const field of fields) {
    const numericValue = Number(router?.[field]);

    if (Number.isFinite(numericValue)) {
      return numericValue;
    }
  }

  return null;
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
    return `${days}d ${hours}h ${minutes}m`;
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
      timeStyle: "medium",
    },
  ).format(date);
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


function MetricCard({
  icon: Icon,
  label,
  value,
}) {
  return (
    <article className="rounded-xl border border-white/[0.07] bg-slate-950/40 p-4">
      <div className="flex items-center gap-2 text-slate-500">
        <Icon className="size-4" />

        <span className="text-xs font-medium uppercase tracking-wider">
          {label}
        </span>
      </div>

      <p className="mt-3 text-xl font-semibold text-white">
        {value}
      </p>
    </article>
  );
}


function DetailField({
  label,
  value,
  icon: Icon,
}) {
  return (
    <div className="flex items-start gap-3 rounded-xl border border-white/[0.06] bg-white/[0.02] p-3">
      <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-white/[0.04] text-slate-500">
        <Icon className="size-4" />
      </div>

      <div className="min-w-0">
        <p className="text-xs font-medium uppercase tracking-wider text-slate-600">
          {label}
        </p>

        <p className="mt-1 break-words text-sm text-slate-300">
          {value ?? "—"}
        </p>
      </div>
    </div>
  );
}


export function RouterDetailDrawer({
  isOpen,
  routerId,
  onClose,
}) {
  const [routerData, setRouterData] =
    useState(null);

  const [isLoading, setIsLoading] =
    useState(false);

  const [error, setError] =
    useState(null);

  const loadRouter = useCallback(async () => {
    if (
      routerId === null
      || routerId === undefined
    ) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const router = await routerService.getById(
        routerId,
      );

      setRouterData(router);
    } catch (requestError) {
      setError(
        requestError?.message
          ?? "Unable to load router details.",
      );
    } finally {
      setIsLoading(false);
    }
  }, [routerId]);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    setRouterData(null);
    loadRouter();
  }, [isOpen, loadRouter]);

  useEffect(() => {
    if (!isOpen) {
      return undefined;
    }

    function handleKeyDown(event) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    window.addEventListener(
      "keydown",
      handleKeyDown,
    );

    return () => {
      window.removeEventListener(
        "keydown",
        handleKeyDown,
      );
    };
  }, [isOpen, onClose]);

  if (!isOpen) {
    return null;
  }

  function handleBackdropClick(event) {
    if (event.target === event.currentTarget) {
      onClose();
    }
  }

  const status = getRouterStatus(routerData);

  const cpuUsage = getPercentage(
    routerData,
    "cpu_usage_percent",
    "cpu_usage",
  );

  const memoryUsage = getPercentage(
    routerData,
    "memory_usage_percent",
    "memory_usage",
  );

  const lastSuccessfulContact =
    routerData?.last_successful_contact_at
    ?? routerData?.last_seen_at
    ?? routerData?.last_online_at
    ?? null;

  return (
    <div
      role="presentation"
      onMouseDown={handleBackdropClick}
      className="fixed inset-0 z-50 flex justify-end bg-slate-950/75 backdrop-blur-sm"
    >
      <aside
        role="dialog"
        aria-modal="true"
        aria-labelledby="router-detail-title"
        className="flex h-full w-full max-w-xl flex-col border-l border-white/10 bg-slate-900 shadow-2xl shadow-black/60"
      >
        <header className="flex items-start justify-between border-b border-white/[0.07] px-5 py-5 sm:px-6">
          <div className="flex min-w-0 items-start gap-3">
            <div className="flex size-11 shrink-0 items-center justify-center rounded-xl border border-emerald-400/20 bg-emerald-400/10">
              <Router className="size-5 text-emerald-400" />
            </div>

            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <h2
                  id="router-detail-title"
                  className="truncate font-semibold text-white"
                >
                  {routerData?.name
                    ?? "Router details"}
                </h2>

                {routerData && (
                  <StatusBadge status={status} />
                )}
              </div>

              <p className="mt-1 text-sm text-slate-500">
                {routerData?.management_ip
                  ?? "Loading device information..."}
              </p>
            </div>
          </div>

          <button
            type="button"
            aria-label="Close router details"
            onClick={onClose}
            className="flex size-9 shrink-0 items-center justify-center rounded-xl text-slate-500 transition hover:bg-white/5 hover:text-white"
          >
            <X className="size-5" />
          </button>
        </header>

        <div className="flex-1 overflow-y-auto">
          {isLoading && !routerData ? (
            <div className="grid min-h-full place-items-center p-8">
              <div className="text-center">
                <LoaderCircle className="mx-auto size-8 animate-spin text-emerald-400" />

                <p className="mt-3 text-sm text-slate-500">
                  Loading router details...
                </p>
              </div>
            </div>
          ) : error && !routerData ? (
            <div className="grid min-h-full place-items-center p-8">
              <div className="max-w-sm text-center">
                <div className="mx-auto flex size-14 items-center justify-center rounded-2xl border border-red-400/20 bg-red-400/10">
                  <AlertTriangle className="size-6 text-red-300" />
                </div>

                <h3 className="mt-5 font-semibold text-white">
                  Unable to load router
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-500">
                  {error}
                </p>

                <button
                  type="button"
                  onClick={loadRouter}
                  className="mx-auto mt-5 flex h-10 items-center justify-center gap-2 rounded-xl bg-emerald-400 px-4 text-sm font-semibold text-slate-950 transition hover:bg-emerald-300"
                >
                  <RefreshCw className="size-4" />
                  Try again
                </button>
              </div>
            </div>
          ) : routerData ? (
            <div className="space-y-6 p-5 sm:p-6">
              {routerData.last_error && (
                <div className="rounded-xl border border-amber-400/20 bg-amber-400/10 px-4 py-3">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="mt-0.5 size-4 shrink-0 text-amber-300" />

                    <div>
                      <p className="text-sm font-medium text-amber-200">
                        Current monitoring error
                      </p>

                      <p className="mt-1 text-xs leading-5 text-amber-300/75">
                        {routerData.last_error}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <section>
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-white">
                    Operational metrics
                  </h3>

                  <button
                    type="button"
                    disabled={isLoading}
                    onClick={loadRouter}
                    className="flex items-center gap-2 rounded-lg border border-white/10 px-3 py-1.5 text-xs font-medium text-slate-400 transition hover:border-white/20 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <RefreshCw
                      className={[
                        "size-3.5",
                        isLoading
                          ? "animate-spin"
                          : "",
                      ].join(" ")}
                    />

                    Refresh
                  </button>
                </div>

                <div className="grid gap-3 sm:grid-cols-3">
                  <MetricCard
                    icon={Cpu}
                    label="CPU"
                    value={formatPercentage(cpuUsage)}
                  />

                  <MetricCard
                    icon={HardDrive}
                    label="Memory"
                    value={formatPercentage(
                      memoryUsage,
                    )}
                  />

                  <MetricCard
                    icon={TimerReset}
                    label="Uptime"
                    value={formatUptime(
                      routerData.uptime_seconds,
                    )}
                  />
                </div>
              </section>

              <section>
                <h3 className="mb-3 text-sm font-semibold text-white">
                  Device information
                </h3>

                <div className="grid gap-3 sm:grid-cols-2">
                  <DetailField
                    icon={Box}
                    label="Model"
                    value={routerData.model}
                  />

                  <DetailField
                    icon={ShieldCheck}
                    label="Identity"
                    value={routerData.identity}
                  />

                  <DetailField
                    icon={Router}
                    label="RouterOS"
                    value={
                      routerData.routeros_version
                    }
                  />

                  <DetailField
                    icon={Network}
                    label="API port"
                    value={routerData.api_port}
                  />
                </div>
              </section>

              <section>
                <h3 className="mb-3 text-sm font-semibold text-white">
                  Network addresses
                </h3>

                <div className="grid gap-3 sm:grid-cols-2">
                  <DetailField
                    icon={Network}
                    label="Management IP"
                    value={
                      routerData.management_ip
                    }
                  />

                  <DetailField
                    icon={Globe2}
                    label="Public IP"
                    value={
                      routerData.public_ip
                        ?? "Not configured"
                    }
                  />
                </div>
              </section>

              <section>
                <h3 className="mb-3 text-sm font-semibold text-white">
                  Monitoring history
                </h3>

                <div className="space-y-3">
                  <DetailField
                    icon={CalendarClock}
                    label="Last checked"
                    value={formatDateTime(
                      routerData.last_checked_at,
                    )}
                  />

                  <DetailField
                    icon={ShieldCheck}
                    label="Last successful contact"
                    value={formatDateTime(
                      lastSuccessfulContact,
                    )}
                  />
                </div>
              </section>
            </div>
          ) : null}
        </div>
      </aside>
    </div>
  );
}