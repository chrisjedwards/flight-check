"use strict";

document.addEventListener("DOMContentLoaded", async () => {
  const app = document.querySelector("#app");
  const status = document.createElement("p");
  status.setAttribute("role", "status");
  status.textContent = "Checking service status...";
  app.append(status);

  try {
    const response = await fetch("/api/health");
    if (!response.ok) {
      throw new Error(`Health check failed with status ${response.status}`);
    }
    const result = await response.json();
    status.textContent = `Service status: ${result.status}`;
  } catch (error) {
    status.textContent = "Service status: unavailable";
    console.error(error);
  }
});
