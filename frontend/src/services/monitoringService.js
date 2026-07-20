import { apiClient } from "../api/client";


export const monitoringService = {
  getStatus() {
    return apiClient.get(
      "/monitoring/status",
    );
  },

  triggerPolling() {
    return apiClient.post(
      "/monitoring/poll",
    );
  },
};