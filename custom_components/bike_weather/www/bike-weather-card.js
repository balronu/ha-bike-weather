/* Bike Weather card v0.1.0-beta.3. */
(function () {
  "use strict";
  const VERSION = "0.1.0-beta.3";
  const registered = window.customCards || (window.customCards = []);
  if (!registered.some((card) => card.type === "bike-weather-card")) {
    registered.push({ type: "bike-weather-card", name: "Bike Weather", description: "Cycling weather score and forecast" });
  }
  const TEXT = {
    de: { title: "Fahrradwetter", loading: "Lade…", unavailable: "Nicht verfügbar", temperature: "Temperatur", wind: "Wind", rain: "Regenrate", forecast: "Prognose", source: "Quelle", quality: "Datenqualität", noForecast: "Keine Prognosedaten", window: "Fahrzeitfenster", duration: "Fahrtdauer", minutes: "Minuten", stale: "Daten fehlen oder sind veraltet", unknown: "unbekannt", entry: "Bike-Weather-Eintrag", showForecast: "Prognose anzeigen", showDetails: "Details anzeigen", start: "Start (HH:MM)" },
    en: { title: "Bike Weather", loading: "Loading…", unavailable: "Unavailable", temperature: "Temperature", wind: "Wind", rain: "Rain rate", forecast: "Forecast", source: "Source", quality: "Data quality", noForecast: "No forecast data", window: "Ride window", duration: "Ride duration", minutes: "minutes", stale: "Data missing or stale", unknown: "unknown", entry: "Bike Weather entry", showForecast: "Show forecast", showDetails: "Show details", start: "Start (HH:MM)" }
  };
  function strings(hass) { return (hass && hass.locale && hass.locale.language || "en").startsWith("de") ? TEXT.de : TEXT.en; }
  function esc(v) { return String(v == null ? "" : v).replace(/[&<>"']/g, (x) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[x])); }
  function value(v, unit) { return v == null ? "—" : `${Number(v).toFixed(1)} ${unit}`; }
  function time(v) { if (!v) return "—"; const d = new Date(v); return Number.isNaN(d.valueOf()) ? "—" : d.toLocaleTimeString([], {hour:"2-digit", minute:"2-digit"}); }
  class BikeWeatherCard extends HTMLElement {
    setConfig(config) { if (!config || !config.entry_id) throw new Error("Bike Weather requires entry_id"); this.config = {show_forecast:true, show_details:true, ride_start:"07:30", ride_duration_minutes:60, ...config}; this.render(); }
    set hass(value) { this._hass = value; if (this.config && this._lastConnection !== value.connection) { this._lastConnection = value.connection; this.refresh(); } }
    async refresh() { this.loading = true; this.render(); try { this.data = await this._hass.callWS({type:"bike_weather/card_data", entry_id:this.config.entry_id}); this.error = null; } catch (err) { this.error = err.message || "Unable to load Bike Weather"; } this.loading = false; this.render(); }
    render() {
      if (!this.shadowRoot) this.attachShadow({mode:"open"});
      const t = strings(this._hass), d = this.data, c = d && d.current || {}, forecast = (d && d.forecast || []).slice(0, 6);
      const status = d ? `${d.assessment || t.unknown} · ${d.score == null ? "—" : d.score}/100` : (this.loading ? t.loading : t.unavailable);
      const stale = !d || d.quality === "stale" || d.quality === "unavailable";
      this.shadowRoot.innerHTML = `<style>:host{display:block;contain:content}.card{padding:16px;border-radius:14px;background:var(--ha-card-background,var(--card-background-color,#fff));color:var(--primary-text-color);box-shadow:var(--ha-card-box-shadow,none);overflow:hidden}.header{display:flex;justify-content:space-between;gap:12px;align-items:center}.title{font-size:1.15em;font-weight:600}.status{color:var(--secondary-text-color);margin-top:4px}.score{font-size:2em;font-weight:700;color:var(--primary-color)}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:14px}.metric,.slot{padding:10px;background:var(--secondary-background-color,#eee);border-radius:10px;min-width:0}.label{font-size:.78em;color:var(--secondary-text-color);overflow-wrap:anywhere}.value{margin-top:3px;font-weight:600}.forecast{display:grid;grid-template-columns:repeat(auto-fit,minmax(72px,1fr));gap:8px;margin-top:8px}.error{color:var(--error-color,#db4437);overflow-wrap:anywhere}.notice{color:var(--warning-color,#a66b00);margin:12px 0 0}.meta{margin-top:12px;font-size:.82em;color:var(--secondary-text-color);overflow-wrap:anywhere}@media(max-width:420px){.card{padding:12px}.grid{gap:6px}.metric{padding:8px}.score{font-size:1.65em}}</style><ha-card class="card"><div class="header"><div><div class="title">${esc(t.title)}</div><div class="status">${esc(status)}</div></div><div class="score">${d && d.score != null ? esc(d.score) : "—"}</div></div>${this.error ? `<p class="error">${esc(this.error)}</p>` : ""}${stale && !this.error ? `<p class="notice">${esc(t.stale)}</p>` : ""}<div class="grid"><div class="metric"><div class="label">${esc(t.temperature)}</div><div class="value">${value(c.temperature_c,"°C")}</div></div><div class="metric"><div class="label">${esc(t.wind)}</div><div class="value">${value(c.wind_kmh,"km/h")}</div></div><div class="metric"><div class="label">${esc(t.rain)}</div><div class="value">${value(c.precipitation_mm,"mm/h")}</div></div></div>${this.config.show_forecast ? `<div class="label" style="margin-top:14px">${esc(t.forecast)}</div><div class="forecast">${forecast.map((slot) => `<div class="slot"><div class="label">${time(slot.datetime)}</div><div class="value">${slot.score == null ? "—" : esc(slot.score)}</div><div class="label">${esc(slot.status || t.unknown)}</div></div>`).join("") || `<div class="label">${esc(t.noForecast)}</div>`}</div>` : ""}${this.config.show_details && d ? `<div class="meta">${esc(t.window)}: ${esc(this.config.ride_start)} · ${esc(this.config.ride_duration_minutes)} ${esc(t.minutes)}<br>${esc(t.source)}: ${esc((d.sources || []).join(", ") || "—")} · ${esc(t.quality)}: ${esc(d.quality || "—")}</div>` : ""}</ha-card>`;
    }
    getCardSize() { return 4; }
    static getConfigElement() { return document.createElement("bike-weather-card-editor"); }
    static getStubConfig() { return {entry_id:"", show_forecast:true, show_details:true, ride_start:"07:30", ride_duration_minutes:60}; }
  }
  class BikeWeatherCardEditor extends HTMLElement {
    setConfig(config) { this.config = {show_forecast:true, show_details:true, ride_start:"07:30", ride_duration_minutes:60, ...config}; this.render(); }
    set hass(value) { this._hass = value; this.render(); }
    render() { const t = strings(this._hass); this.innerHTML = `<style>:host{display:block;padding:8px}.row{display:block;margin:8px 0}input{width:100%;box-sizing:border-box}</style><label class="row">${esc(t.entry)}<input data-key="entry_id" value="${esc(this.config.entry_id)}"></label><label class="row">${esc(t.start)}<input data-key="ride_start" value="${esc(this.config.ride_start)}"></label><label class="row">${esc(t.duration)}<input type="number" min="1" max="1440" data-key="ride_duration_minutes" value="${esc(this.config.ride_duration_minutes)}"></label><label class="row"><input type="checkbox" data-key="show_forecast" ${this.config.show_forecast ? "checked" : ""}> ${esc(t.showForecast)}</label><label class="row"><input type="checkbox" data-key="show_details" ${this.config.show_details ? "checked" : ""}> ${esc(t.showDetails)}</label>`; this.querySelectorAll("[data-key]").forEach((el) => el.addEventListener("change", () => { const key=el.dataset.key; this.config[key] = el.type === "checkbox" ? el.checked : (el.type === "number" ? Number(el.value) : el.value); this.dispatchEvent(new CustomEvent("config-changed", {bubbles:true, composed:true, detail:{config:{...this.config}}})); })); }
  }
  if (!customElements.get("bike-weather-card")) customElements.define("bike-weather-card", BikeWeatherCard);
  if (!customElements.get("bike-weather-card-editor")) customElements.define("bike-weather-card-editor", BikeWeatherCardEditor);
  window.BIKE_WEATHER_CARD_VERSION = VERSION;
})();
