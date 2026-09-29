"use strict";

import { ApiError, fetchAirports, fetchFlights } from "./api.js";
import { createFlightTable, renderFlightDetails } from "./render.js";

const PAGE_SIZE = 50;
const REFRESH_INTERVAL_MS = 60_000;
const CONTINENT_ORDER = ["Africa", "Asia", "Europe", "North America", "Oceania", "South America", "Antarctica"];
const elements = {
  airport: document.querySelector("#airport-select"),
  date: document.querySelector("#date-select"),
  refresh: document.querySelector("#refresh-button"),
  directionTabs: [...document.querySelectorAll("[data-direction]")],
  search: document.querySelector("#flight-search"),
  continent: document.querySelector("#continent-select"),
  upcoming: document.querySelector("#upcoming-only"),
  count: document.querySelector("#flight-count"),
  updated: document.querySelector("#last-updated"),
    refreshSpinner: document.querySelector("#refresh-spinner"),
    fromTime: document.querySelector("#from-time"),
    now: document.querySelector("#now-button"),
    quickFilters: [...document.querySelectorAll("[data-show]")],
    clearFilters: document.querySelector("#clear-filters"),
  error: document.querySelector("#error-container"),
  results: document.querySelector("#flight-region"),
  pagination: document.querySelector("#pagination-region"),
  details: document.querySelector("#flight-details"),
  detailsTitle: document.querySelector("#flight-details-title"),
  detailsBody: document.querySelector("#flight-details-body"),
};

const query = new URLSearchParams(window.location.search);
const state = {
  airports: [],
  airport: query.get("airport") || "ARN",
  direction: query.get("direction") === "departures" ? "departures" : "arrivals",
  date: query.get("date") || todayInStockholm(),
  time: query.get("time") || "",
  show: ["all", "upcoming", "delayed", "cancelled"].includes(query.get("show"))
    ? query.get("show")
    : defaultShowForDate(query.get("date") || todayInStockholm()),
  flights: [],
  visibleLimit: PAGE_SIZE,
  requestNumber: 0,
  hasLoaded: false,
};

let lastFocusedRow = null;

function defaultShowForDate(date) {
  return date === todayInStockholm() ? "upcoming" : "all";
}

function todayInStockholm() {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Europe/Stockholm",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(new Date());
  const values = Object.fromEntries(parts.map((part) => [part.type, part.value]));
  return `${values.year}-${values.month}-${values.day}`;
}

function setDirection(direction) {
  state.direction = direction;
  elements.directionTabs.forEach((tab) => {
    const active = tab.dataset.direction === direction;
    tab.classList.toggle("active", active);
    tab.setAttribute("aria-selected", String(active));
  });
}

function updateUrl() {
  const params = new URLSearchParams({
    airport: state.airport,
    direction: state.direction,
    date: state.date,
  });
  if (state.time) params.set("time", state.time);
  params.set("show", state.show);
  window.history.replaceState(null, "", `${window.location.pathname}?${params}`);
}

function fillAirportOptions() {
  const options = state.airports.map((airport) => ({
    code: airport.code,
    name: airport.name,
  }));
  if (!options.some((airport) => airport.code === state.airport)) {
    options.unshift({ code: state.airport, name: `Unknown airport (${state.airport})` });
  }

  elements.airport.replaceChildren();
  options.forEach((airport) => {
    const option = document.createElement("option");
    option.value = airport.code;
    option.textContent = `${airport.code} · ${airport.name}`;
    elements.airport.append(option);
  });
  elements.airport.value = state.airport;
}

function showLoading(preserveCurrent) {
  elements.results.setAttribute("aria-busy", "true");
  if (state.hasLoaded && preserveCurrent) {
    elements.count.textContent = "Updating flights…";
    return;
  }

  const loading = document.createElement("div");
  loading.className = "loading-state";
  loading.setAttribute("role", "status");
  const spinner = document.createElement("span");
  spinner.className = "spinner-border spinner-border-sm";
  spinner.setAttribute("aria-hidden", "true");
  const label = document.createElement("span");
  label.textContent = "Loading flights…";
  loading.append(spinner, label);
  elements.results.replaceChildren(loading);
  elements.count.textContent = "Loading flights…";
}

function showError(error) {
  elements.error.replaceChildren();
  const alert = document.createElement("div");
  alert.className = "alert alert-danger api-alert mb-0";
  alert.setAttribute("role", "alert");

  const message = document.createElement("span");
  message.textContent = error instanceof ApiError
    ? error.message
    : error.message || "Could not load flights. Check your connection and try again.";

  const retry = document.createElement("button");
  retry.className = "btn btn-sm btn-outline-danger";
  retry.type = "button";
  retry.textContent = "Retry";
  retry.addEventListener("click", () => loadFlights(state.hasLoaded));
  alert.append(message, retry);
  elements.error.append(alert);
}

function clearError() {
  elements.error.replaceChildren();
}

function getFilteredFlights() {
  const search = elements.search.value.trim().toLocaleLowerCase();
  const fromTime = elements.fromTime.value;

  return state.flights.filter((flight) => {
    const matchesSearch = !search || [flight.flightId, flight.city, flight.country, flight.airline, flight.continent]
      .some((value) => String(value || "").toLocaleLowerCase().includes(search));
    const matchesTime = !fromTime || Boolean(flight.bestLocal && flight.bestLocal >= fromTime);
    const matchesQuickFilter = state.show === "all"
      || (state.show === "upcoming" && flight.isUpcoming)
      || (state.show === "delayed" && flight.statusCategory === "delayed")
      || (state.show === "cancelled" && flight.statusCategory === "cancelled");
    return matchesSearch && matchesTime && matchesQuickFilter;
  });
}

function updateQuickFilterButtons() {
  elements.quickFilters.forEach((button) => {
    const active = button.dataset.show === state.show;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
}

function updateTimeControls() {
  elements.now.disabled = state.date !== todayInStockholm();
}

function updateClearFiltersVisibility() {
  const hasFilters = elements.search.value.trim() !== ""
    || elements.fromTime.value !== ""
    || state.show !== defaultShowForDate(state.date);
  elements.clearFilters.classList.toggle("d-none", !hasFilters);
}

function showEmpty(title, description) {
  const empty = document.createElement("div");
  empty.className = "empty-state";
  empty.setAttribute("role", "status");
  const heading = document.createElement("strong");
  heading.textContent = title;
  const detail = document.createElement("span");
  detail.textContent = description;
  empty.append(heading, detail);
  elements.results.replaceChildren(empty);
}

function renderFlights() {
  const matches = getFilteredFlights();
  const visibleFlights = matches.slice(0, state.visibleLimit);
  elements.count.textContent = `Showing ${visibleFlights.length} of ${matches.length} flights`;
  elements.results.setAttribute("aria-busy", "false");
  elements.pagination.replaceChildren();
  updateClearFiltersVisibility();

  if (state.flights.length === 0) {
    showEmpty("No flights found", "There are no flights for this airport and date.");
    return;
  }
  if (matches.length === 0) {
    showEmpty("No matching flights", "Try changing your search or filters.");
    return;
  }

  elements.results.replaceChildren(
    createFlightTable(visibleFlights, state.direction, openFlightDetails),
  );
  if (visibleFlights.length < matches.length) {
    const more = document.createElement("button");
    more.className = "btn btn-outline-secondary btn-sm px-4";
    more.type = "button";
    more.textContent = `Show more (${Math.min(PAGE_SIZE, matches.length - visibleFlights.length)})`;
    more.addEventListener("click", () => {
      state.visibleLimit += PAGE_SIZE;
      renderFlights();
    });
    elements.pagination.append(more);
  }
}

function updateLastUpdated() {
  elements.updated.textContent = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Europe/Stockholm",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(new Date());
}

function openFlightDetails(flight, row) {
  const airport = state.airports.find((item) => item.code === state.airport)
    || { code: state.airport, name: state.airport };
  lastFocusedRow = row;
  renderFlightDetails(
    elements.detailsTitle,
    elements.detailsBody,
    flight,
    state.direction,
    airport,
  );
  window.bootstrap.Offcanvas.getOrCreateInstance(elements.details).show();
}

async function loadFlights(preserveCurrent = true) {
  const requestNumber = ++state.requestNumber;
  const previousScroll = window.scrollY;
  clearError();
  showLoading(preserveCurrent);
  elements.refresh.disabled = true;
  elements.refreshSpinner.classList.remove("d-none");

  try {
    const flights = await fetchFlights(state.airport, state.direction, state.date);
    if (requestNumber !== state.requestNumber) return;
    state.flights = flights;
    if (!preserveCurrent) state.visibleLimit = PAGE_SIZE;
    state.hasLoaded = true;
    updateTimeControls();
    updateLastUpdated();
    updateUrl();
    renderFlights();
    window.requestAnimationFrame(() => window.scrollTo(0, previousScroll));
  } catch (error) {
    if (requestNumber !== state.requestNumber) return;
    elements.results.setAttribute("aria-busy", "false");
    showError(error);
    if (preserveCurrent && state.hasLoaded) {
      renderFlights();
    } else {
      state.flights = [];
      state.hasLoaded = false;
      elements.pagination.replaceChildren();
      elements.count.textContent = "Flights could not be loaded";
      elements.results.replaceChildren();
    }
  } finally {
    if (requestNumber === state.requestNumber) {
      elements.refresh.disabled = false;
      elements.refreshSpinner.classList.add("d-none");
    }
  }
}

function handleSelectionChange() {
  const previousDate = state.date;
  state.airport = elements.airport.value;
  state.date = elements.date.value;
  if (state.date !== previousDate) state.show = defaultShowForDate(state.date);
  state.visibleLimit = PAGE_SIZE;
  updateQuickFilterButtons();
  updateTimeControls();
  updateUrl();
  loadFlights(false);
}

async function initialize() {
  elements.date.value = state.date;
  elements.fromTime.value = state.time;
  setDirection(state.direction);
  updateQuickFilterButtons();
  updateTimeControls();
  fillAirportOptions();

  try {
    state.airports = await fetchAirports();
    fillAirportOptions();
    await loadFlights();
  } catch (error) {
    elements.results.setAttribute("aria-busy", "false");
    elements.count.textContent = "Airports could not be loaded";
    showError(error);
  }
}

elements.airport.addEventListener("change", handleSelectionChange);
elements.date.addEventListener("change", handleSelectionChange);
elements.fromTime.addEventListener("input", () => {
  state.time = elements.fromTime.value;
  state.visibleLimit = PAGE_SIZE;
  updateUrl();
  renderFlights();
});
elements.now.addEventListener("click", () => {
  elements.fromTime.value = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Europe/Stockholm",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(new Date());
  elements.fromTime.dispatchEvent(new Event("input", { bubbles: true }));
});
elements.refresh.addEventListener("click", () => loadFlights());
elements.directionTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    setDirection(tab.dataset.direction);
    state.visibleLimit = PAGE_SIZE;
    updateUrl();
    loadFlights(false);
  });
});
elements.quickFilters.forEach((button) => {
  button.addEventListener("click", () => {
    state.show = button.dataset.show;
    state.visibleLimit = PAGE_SIZE;
    updateQuickFilterButtons();
    updateUrl();
    renderFlights();
  });
});
elements.search.addEventListener("input", () => {
  state.visibleLimit = PAGE_SIZE;
  renderFlights();
});
elements.clearFilters.addEventListener("click", () => {
  elements.search.value = "";
  elements.fromTime.value = "";
  state.time = "";
  state.show = defaultShowForDate(state.date);
  state.visibleLimit = PAGE_SIZE;
  updateQuickFilterButtons();
  updateUrl();
  renderFlights();
});

elements.details.addEventListener("hidden.bs.offcanvas", () => {
  if (lastFocusedRow?.isConnected) lastFocusedRow.focus();
  lastFocusedRow = null;
});

initialize();
window.setInterval(() => loadFlights(), REFRESH_INTERVAL_MS);
