/* Bike Weather card v0.1.0-beta.1. No scoring logic lives in this bundle. */
(function () {
  "use strict";
  const VERSION = "0.1.0-beta.1";
  const registered = window.customCards || (window.customCards = []);
  if (!registered.some((card) => card.type === "bike-weather-card")) {
    registered.push({ type: "bike-weather-card", name: "Bike Weather", description: "Bike weather assessment" });
  }
  class BikeWeatherCard extends HTMLElement {
    setConfig(config) {
      if (!config || !config.entry_id) throw new Error("Bike Weather requires entry_id");
      this.config = { compact: false, show_forecast: true, show_windows: true, show_details: true, ...config };
      this.render();
    }
    set hass(value) {
      this._hass = value;
      if (this.config && this._lastConnection !== value.connection) {
        this._lastConnection = value.connection;
        this.refresh();
      }
    }
    async refresh() {
      this.loading = true; this.render();
      try {
        this.data = await this._hass.callWS({ type: "bike_weather/card_data", entry_id: this.config.entry_id });
        this.error = null;
      } catch (err) { this.error = err.message || "Unable to load Bike Weather"; }
      this.loading = false; this.render();
    }
    render() {
      if (!this.shadowRoot) this.attachShadow({ mode: "open" });
      const d = this.data;
      const status = d ? `${d.assessment} · ${d.score == null ? "—" : d.score}/100` : (this.loading ? "Loading…" : "Unavailable");
      const c = d && d.current ? d.current : {};
      this.shadowRoot.innerHTML = `<style>
        :host{display:block}.card{padding:16px;border-radius:12px;background:var(--ha-card-background,var(--card-background-color,#fff));color:var(--primary-text-color);box-shadow:var(--ha-card-box-shadow,none)}
        .header{display:flex;justify-content:space-between;gap:12px;align-items:center}.score{font-size:1.7em;font-weight:700}.status{text-transform:capitalize}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(100px,1fr));gap:8px;margin-top:14px}.metric{padding:8px;background:var(--secondary-background-color,#eee);border-radius:8px}.label{font-size:.8em;color:var(--secondary-text-color)}.error{color:var(--error-color,#db4437)}
      </style><ha-card class="card"><div class="header"><div><div class="label">Bike Weather</div><div class="status">${escapeHtml(status)}</div></div><div class="score">${d && d.score != null ? d.score : "—"}</div></div>
      ${this.error ? `<p class="error">${escapeHtml(this.error)}</p>` : ""}<div class="grid"><div class="metric"><div class="label">Temperature</div>${value(c.temperature_c, "°C")}</div><div class="metric"><div class="label">Wind</div>${value(c.wind_kmh, "km/h")}</div><div class="metric"><div class="label">Rain</div>${value(c.precipitation_mm, "mm")}</div></div>
      ${d && this.config.show_forecast ? `<div class="label" style="margin-top:12px">Forecast</div><div class="grid">${(d.forecast || []).slice(0, 6).map((slot) => `<div class="metric"><div class="label">${formatTime(slot.datetime)}</div><strong>${slot.score == null ? "—" : slot.score}</strong><div>${escapeHtml(slot.status || "unknown")}</div></div>`).join("") || "<div class=label>No forecast data</div>"}</div>` : ""}
      ${d && this.config.show_details ? `<div class="label" style="margin-top:12px">Source: ${escapeHtml((d.sources || []).join(", ") || "—")} · ${escapeHtml(d.quality || "—")}</div>` : ""}</ha-card>`;
    }
    getCardSize() { return 3; }
    getConfigElement() { return document.createElement("bike-weather-card-editor"); }
    getStubConfig() { return { entry_id: "", show_forecast: true, show_windows: true, show_details: true }; }
  }
  function value(v, unit) { return v == null ? "—" : `${Number(v).toFixed(1)} ${unit}`; }
  function formatTime(v) { if (!v) return "—"; const d = new Date(v); return Number.isNaN(d.valueOf()) ? "—" : d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }); }
  function escapeHtml(v) { return String(v).replace(/[&<>"']/g, (x) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[x])); }
  if (!customElements.get("bike-weather-card")) customElements.define("bike-weather-card", BikeWeatherCard);
  class BikeWeatherCardEditor extends HTMLElement {
    setConfig(config) { this.config = { ...config }; this.innerHTML = `<label>Bike Weather entry ID <input value="${escapeHtml(this.config.entry_id || "")}"></label>`; this.querySelector("input").addEventListener("change", (event) => { this.config.entry_id = event.target.value; this.dispatchEvent(new CustomEvent("config-changed", { bubbles: true, composed: true, detail: { config: this.config } })); }); }
  }
  if (!customElements.get("bike-weather-card-editor")) customElements.define("bike-weather-card-editor", BikeWeatherCardEditor);
  window.BIKE_WEATHER_CARD_VERSION = VERSION;
})();
