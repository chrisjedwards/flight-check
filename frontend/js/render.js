"use strict";

const MISSING = "—";

function element(tagName, className = "", text = null) {
  const node = document.createElement(tagName);
  if (className) node.className = className;
  if (text !== null) node.textContent = text;
  return node;
}

function flagFor(countryCode) {
  if (!/^[A-Z]{2}$/.test(countryCode || "")) return "";
  return [...countryCode].map((letter) => String.fromCodePoint(127397 + letter.charCodeAt(0))).join("");
}

function appendTextLine(parent, className, value) {
  const line = element("span", className, value || MISSING);
  parent.append(line);
  return line;
}

function createTimeCell(flight) {
  const cell = element("td", "time-cell");
  const scheduled = flight.scheduled || MISSING;
  const estimateDiffers = flight.estimated && flight.estimated !== flight.scheduled;

  if (estimateDiffers) {
    cell.append(element("s", "scheduled-time", scheduled));
    appendTextLine(cell, "estimated-time", flight.estimated);
  } else {
    appendTextLine(cell, "scheduled-time", scheduled);
  }

  if (flight.actual) appendTextLine(cell, "actual-time", `Actual ${flight.actual}`);
  return cell;
}

function createFlightCell(flight) {
  const cell = element("td", "flight-cell");
  appendTextLine(cell, "flight-number", flight.flightId || MISSING);
  appendTextLine(cell, "flight-airline", flight.airline);
  return cell;
}

function createRouteCell(flight) {
  const cell = element("td", "route-cell");
  const mainLine = element("span", "route-main");
  const flag = flagFor(flight.countryCode);
  if (flag) mainLine.append(element("span", "route-flag", flag));
  mainLine.append(element("span", "route-city", flight.city || MISSING));
  cell.append(mainLine);

  appendTextLine(cell, "route-country", flight.country);
  if (flight.via && flight.via.length > 0) {
    appendTextLine(cell, "route-via", `via ${flight.via.join(", ")}`);
  }
  return cell;
}

function createLocationCell(flight) {
  const cell = element("td", "location-cell d-none d-md-table-cell");
  const terminal = flight.terminal
    ? (flight.terminal.startsWith("T") ? flight.terminal : `T${flight.terminal}`)
    : null;
  const gate = flight.gate ? `Gate ${flight.gate}` : null;
  const location = [terminal, gate].filter(Boolean).join(" · ");
  cell.textContent = location || MISSING;
  return cell;
}

function statusPresentation(flight) {
  if (flight.statusCategory === "delayed" && Number.isFinite(flight.delayMinutes)) {
    return { label: `Delayed +${flight.delayMinutes} min`, style: "status-delayed" };
  }
  const statusStyles = {
    LAN: "text-bg-success",
    CAN: "text-bg-danger",
    SCH: "text-bg-primary",
  };
  return {
    label: flight.status === "ACT" ? "Departed" : flight.statusText || flight.status || MISSING,
    style: statusStyles[flight.status] || "text-bg-secondary",
  };
}

function createStatusCell(flight) {
  const cell = element("td", "status-cell");
  const presentation = statusPresentation(flight);
  cell.append(element("span", `badge status-badge ${presentation.style}`, presentation.label));
  for (const remark of flight.remarks || []) {
    if (remark && remark !== presentation.label && remark !== flight.statusText) {
      appendTextLine(cell, "flight-remark", remark);
    }
  }
  return cell;
}

function createBaggageCell(flight) {
  const cell = element("td", "baggage-cell");
  cell.textContent = flight.baggage || MISSING;
  return cell;
}

export function createFlightTable(flights, direction, onSelectFlight) {
  const wrapper = element("div", "table-responsive board-table-wrap");
  const table = element("table", "table align-middle flight-table mb-0");
  const head = element("thead");
  const headerRow = element("tr");
  const headers = ["Time", "Flight", direction === "arrivals" ? "From" : "To", "Terminal / Gate"];
  if (direction === "arrivals") headers.push("Baggage belt");
  headers.push("Status");

  headers.forEach((label) => {
    const header = element("th", "", label);
    header.scope = "col";
    if (label === "Terminal / Gate") header.classList.add("d-none", "d-md-table-cell");
    headerRow.append(header);
  });
  head.append(headerRow);

  const body = element("tbody");
  flights.forEach((flight) => {
    const row = element("tr", flight.isCancelled ? "flight-row is-cancelled" : "flight-row");
    row.tabIndex = 0;
    row.setAttribute("role", "button");
    row.setAttribute("aria-haspopup", "dialog");
    row.setAttribute(
      "aria-label",
      `Flight ${flight.flightId || MISSING}, ${direction === "arrivals" ? "from" : "to"} ${flight.city || MISSING}. Open details.`,
    );
    row.addEventListener("click", () => onSelectFlight(flight, row));
    row.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        onSelectFlight(flight, row);
      }
    });
    if (flight.statusCategory === "delayed") {
      row.classList.add("is-delayed");
    }
    row.append(createTimeCell(flight));
    row.append(createFlightCell(flight));
    row.append(createRouteCell(flight));
    row.append(createLocationCell(flight));
    if (direction === "arrivals") row.append(createBaggageCell(flight));
    row.append(createStatusCell(flight));
    body.append(row);
  });

  table.append(head, body);
  wrapper.append(table);
  return wrapper;
}

function addDetailValue(list, label, value) {
  const item = element("div", "detail-pair");
  item.append(element("dt", "", label));
  item.append(element("dd", "", value === null || value === undefined || value === "" ? MISSING : String(value)));
  list.append(item);
}

function addDetailsSection(container, title, entries) {
  const section = element("section", "detail-section");
  section.append(element("h3", "detail-section-title", title));
  const list = element("dl", "detail-list");
  entries.forEach(([label, value]) => addDetailValue(list, label, value));
  section.append(list);
  container.append(section);
}

function formatAirport(flight, useSelectedAirport, selectedAirport) {
  const airport = useSelectedAirport
    ? { code: selectedAirport.code, name: selectedAirport.name, country: "Sweden", continent: "Europe", countryCode: "SE" }
    : {
      code: flight.cityIata,
      name: flight.city,
      country: flight.country,
      continent: flight.continent,
      countryCode: flight.countryCode,
    };
  const flag = flagFor(airport.countryCode);
  return [
    flag,
    airport.name || MISSING,
    airport.code ? `(${airport.code})` : MISSING,
    airport.country || MISSING,
    airport.continent || MISSING,
  ].filter(Boolean).join(" · ");
}

export function renderFlightDetails(title, body, flight, direction, selectedAirport) {
  title.textContent = [flight.flightId || MISSING, flight.airline || MISSING].join(" · ");
  body.replaceChildren();

  const otherAirportFrom = direction === "arrivals";
  const regionLabels = { D: "Domestic", S: "Schengen", I: "International" };
  const regionExplanations = {
    D: "connects airports within the same country.",
    S: "travels within the Schengen Area.",
    I: "travels outside the Schengen Area.",
  };
  const regionValue = flight.region
    ? `${regionLabels[flight.region] || MISSING}: ${regionExplanations[flight.region] || ""}`.trim()
    : MISSING;
  const routeEntries = [
    ["From", formatAirport(flight, !otherAirportFrom, selectedAirport)],
    ["To", formatAirport(flight, otherAirportFrom, selectedAirport)],
    ["Region", regionValue],
  ];
  addDetailsSection(body, "Route", routeEntries);

  const statusText = flight.status === "ACT" ? "Departed" : flight.statusText || flight.status;
  const delay = flight.delayMinutes === null || flight.delayMinutes === undefined
    ? MISSING
    : `${flight.delayMinutes} min${flight.delayMinutes < 0 ? " (early)" : ""}`;
  addDetailsSection(body, "Times", [
    ["Status", statusText],
    ["Scheduled", flight.scheduled],
    ["Estimated", flight.estimated],
    ["Actual", flight.actual],
    ["Delay", delay],
  ]);

  const locationEntries = [["Terminal", flight.terminal], ["Gate", flight.gate]];
  if (direction === "arrivals") {
    locationEntries.push(["Baggage belt", flight.baggage]);
    locationEntries.push(["First bag", flight.firstBag]);
    locationEntries.push(["Last bag", flight.lastBag]);
  }
  addDetailsSection(body, "Airport details", locationEntries);
  addDetailsSection(body, "Stopovers", [["Via", (flight.via || []).join(", ") || MISSING]]);
  addDetailsSection(body, "Codeshares", [["Flight numbers", (flight.codeShares || []).join(", ") || MISSING]]);

  const remarksSection = element("section", "detail-section");
  remarksSection.append(element("h3", "detail-section-title", "Remarks"));
  const remarks = flight.remarks || [];
  if (remarks.length) {
    const list = element("ul", "detail-remarks");
    remarks.forEach((remark) => list.append(element("li", "", remark)));
    remarksSection.append(list);
  } else {
    remarksSection.append(element("p", "detail-muted mb-0", MISSING));
  }
  body.append(remarksSection);
}
