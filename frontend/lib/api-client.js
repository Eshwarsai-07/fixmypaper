/**
 * Standardized API client for Next.js <-> FastAPI communication.
 * Handles base URLs, global error catching, and timeouts.
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

async function request(endpoint, options = {}) {
  const url = endpoint.startsWith("http") ? endpoint : `${BASE_URL}${endpoint}`;
  
  const defaultHeaders = {
    "Accept": "application/json",
  };

  if (!(options.body instanceof FormData)) {
    defaultHeaders["Content-Type"] = "application/json";
  }

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new ApiError(data.detail || data.error || "An unexpected error occurred", response.status, data);
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    
    // Handle network errors or timeouts
    throw new ApiError(error.message || "Network request failed", 500, null);
  }
}

export const api = {
  get: (url, options) => request(url, { ...options, method: "GET" }),
  post: (url, body, options) => request(url, { ...options, method: "POST", body: body instanceof FormData ? body : JSON.stringify(body) }),
  put: (url, body, options) => request(url, { ...options, method: "PUT", body: body instanceof FormData ? body : JSON.stringify(body) }),
  delete: (url, options) => request(url, { ...options, method: "DELETE" }),
};
