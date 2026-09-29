"use strict";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function requestJson(path) {
  const response = await fetch(path, {
    headers: { Accept: "application/json" },
  });

  let payload;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const detail = payload && typeof payload.detail === "string"
      ? payload.detail
      : `Request failed with status ${response.status}`;
    throw new ApiError(detail, response.status);
  }

  return payload;
}

export function fetchAirports() {
  return requestJson("/api/airports");
}

export function fetchFlights(airport, direction, date) {
  const path = `/api/flights/${encodeURIComponent(airport)}/${encodeURIComponent(direction)}/${encodeURIComponent(date)}`;
  return requestJson(path);
}
