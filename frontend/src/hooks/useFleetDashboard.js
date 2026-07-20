import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import { monitoringService } from "../services/monitoringService";
import { routerService } from "../services/routerService";


const REFRESH_INTERVAL_MS = 15_000;


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


export function useFleetDashboard() {
  const [routers, setRouters] = useState([]);
  const [monitoringStatus, setMonitoringStatus] =
    useState(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] =
    useState(false);

  const [error, setError] = useState(null);
  const [lastUpdatedAt, setLastUpdatedAt] =
    useState(null);

  const loadDashboard = useCallback(
    async ({ silent = false } = {}) => {
      if (silent) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }

      setError(null);

      const [
        routersResult,
        monitoringResult,
      ] = await Promise.allSettled([
        routerService.list({
          page: 1,
          pageSize: 100,
        }),
        monitoringService.getStatus(),
      ]);

      const errors = [];

      if (routersResult.status === "fulfilled") {
        setRouters(routersResult.value.items);
      } else {
        errors.push(
          routersResult.reason?.message
            ?? "Unable to load routers.",
        );
      }

      if (monitoringResult.status === "fulfilled") {
        setMonitoringStatus(
          monitoringResult.value,
        );
      } else {
        errors.push(
          monitoringResult.reason?.message
            ?? "Unable to load monitoring status.",
        );
      }

      if (errors.length > 0) {
        setError(errors.join(" "));
      } else {
        setLastUpdatedAt(new Date());
      }

      setIsLoading(false);
      setIsRefreshing(false);
    },
    [],
  );

  useEffect(() => {
    loadDashboard();

    const intervalId = window.setInterval(
      () => {
        loadDashboard({
          silent: true,
        });
      },
      REFRESH_INTERVAL_MS,
    );

    return () => {
      window.clearInterval(intervalId);
    };
  }, [loadDashboard]);

  const statistics = useMemo(() => {
    const activeRouters = routers.filter(
      (router) => router.is_active !== false,
    );

    const online = activeRouters.filter(
      (router) => getRouterStatus(router) === "online",
    ).length;

    const offline = activeRouters.filter(
      (router) => getRouterStatus(router) === "offline",
    ).length;

    const cpuAlerts = activeRouters.filter(
      (router) => {
        const cpuUsage = getCpuUsage(router);

        return cpuUsage !== null && cpuUsage >= 80;
      },
    ).length;

    return {
      total: activeRouters.length,
      online,
      offline,
      cpuAlerts,
    };
  }, [routers]);

  return {
    routers,
    monitoringStatus,
    statistics,
    isLoading,
    isRefreshing,
    error,
    lastUpdatedAt,
    refresh: loadDashboard,
  };
}