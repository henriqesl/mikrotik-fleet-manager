import { apiClient } from "../api/client";


function normalizeRouterList(response) {
  if (Array.isArray(response)) {
    return {
      items: response,
      total: response.length,
      page: 1,
      pageSize: response.length,
    };
  }

  const items =
    response?.items
    ?? response?.routers
    ?? response?.results
    ?? [];

  return {
    items,
    total: response?.total ?? items.length,
    page: response?.page ?? 1,
    pageSize:
      response?.page_size
      ?? response?.pageSize
      ?? items.length,
  };
}


export const routerService = {
  async list({
    page = 1,
    pageSize = 100,
    includeInactive = false,
  } = {}) {
    const response = await apiClient.get(
      "/routers",
      {
        query: {
          page,
          page_size: pageSize,
          include_inactive: includeInactive,
        },
      },
    );

    return normalizeRouterList(response);
  },

  getById(routerId) {
    return apiClient.get(
      `/routers/${routerId}`,
    );
  },

  create(routerData) {
    return apiClient.post(
      "/routers",
      routerData,
    );
  },

  update(routerId, routerData) {
    return apiClient.patch(
      `/routers/${routerId}`,
      routerData,
    );
  },

  deactivate(routerId) {
    return apiClient.delete(
      `/routers/${routerId}`,
    );
  },
};