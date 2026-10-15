/* Bike Weather card v0.1.0-beta.7. */
(function () {
  "use strict";
  const VERSION = "0.1.0-beta.7";
  const LIST_ENTRIES = "bike_weather/list_entries";
  const CARD_DATA = "bike_weather/card_data";
  const DEFAULT_CONFIG = {show_forecast:true, show_details:true, ride_start:"07:30", ride_duration_minutes:60};
  const registered = window.customCards || (window.customCards = []);
  if (!registered.some((card) => card.type === "bike-weather-card")) {
    registered.push({type:"bike-weather-card", name:"Bike Weather", description:"Cycling weather score and forecast"});
  }
  const TEXT = {
    de: {title:"Fahrradwetter", loading:"Lade…", unavailable:"Nicht verfügbar", connectionError:"Kartendaten konnten nicht geladen werden", temperature:"Temperatur", wind:"Wind", rain:"Regenrate", forecast:"Prognose", source:"Quelle", quality:"Datenqualität", noForecast:"Keine Prognosedaten", window:"Fahrzeitfenster", duration:"Fahrtdauer", minutes:"Minuten", stale:"Daten fehlen oder sind veraltet", unknown:"unbekannt", good:"gut", bad:"nicht geeignet", partial:"unvollständig", staleQuality:"veraltet", unavailableQuality:"nicht verfügbar", invalid:"ungültig", local:"Lokale Wetterstation", ha_weather:"Home-Assistant-Wetter", openweathermap:"OpenWeatherMap", providerError:"Wetteranbieter nicht erreichbar", weatherUnavailable:"Home-Assistant-Wetterdaten nicht verfügbar", invalidEntry:"Die konfigurierte Bike-Weather-Integration wurde nicht gefunden.", noEntry:"Keine Bike-Weather-Integration verfügbar.", chooseEntry:"Mehrere Bike-Weather-Integrationen gefunden. Bitte eine auswählen.", entryLoading:"Bike-Weather-Integrationen werden geladen…", entryAuto:"Automatisch erkannte Integration", entryUnavailable:"Integration nicht geladen", entryError:"Integrationen konnten nicht ermittelt werden", entry:"Bike-Weather-Eintrag", showForecast:"Prognose anzeigen", showDetails:"Details anzeigen", start:"Start (HH:MM)"},
    en: {title:"Bike Weather", loading:"Loading…", unavailable:"Unavailable", connectionError:"Card data could not be loaded", temperature:"Temperature", wind:"Wind", rain:"Rain rate", forecast:"Forecast", source:"Source", quality:"Data quality", noForecast:"No forecast data", window:"Ride window", duration:"Ride duration", minutes:"minutes", stale:"Data missing or stale", unknown:"unknown", good:"good", bad:"not suitable", partial:"partial", staleQuality:"stale", unavailableQuality:"unavailable", invalid:"invalid", local:"Local weather station", ha_weather:"Home Assistant weather", openweathermap:"OpenWeatherMap", providerError:"Weather provider unavailable", weatherUnavailable:"Home Assistant weather data unavailable", invalidEntry:"The configured Bike Weather integration was not found.", noEntry:"No Bike Weather integration is available.", chooseEntry:"Multiple Bike Weather integrations were found. Select one.", entryLoading:"Loading Bike Weather integrations…", entryAuto:"Automatically detected integration", entryUnavailable:"Integration is not loaded", entryError:"Integrations could not be loaded", entry:"Bike Weather entry", showForecast:"Show forecast", showDetails:"Show details", start:"Start (HH:MM)"}
  };
  function strings(hass) { return (hass && hass.locale && hass.locale.language || "en").startsWith("de") ? TEXT.de : TEXT.en; }
  function translatedStatus(status, t) { return t[status] || t.unknown; }
  function translatedQuality(quality, t) { return ({good:t.good, partial:t.partial, stale:t.staleQuality, unavailable:t.unavailableQuality, invalid:t.invalid}[quality]) || t.unknown; }
  function translatedSource(source, t) { return t[source] || t.unknown; }
  function translatedError(error, t) { return ({provider_error:t.providerError, ha_weather_unavailable:t.weatherUnavailable, ha_forecast_unavailable:t.noForecast}[error]) || t.unknown; }
  function esc(v) { return String(v == null ? "" : v).replace(/[&<>"']/g, (x) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[x])); }
  function value(v, unit) { return v == null ? "—" : `${Number(v).toFixed(1)} ${unit}`; }
  function time(v) { if (!v) return "—"; const d = new Date(v); return Number.isNaN(d.valueOf()) ? "—" : d.toLocaleTimeString([], {hour:"2-digit", minute:"2-digit"}); }
  function entryLabel(entry, duplicates) { return `${entry.title || "Bike Weather"}${duplicates[entry.title] > 1 ? ` (${entry.entry_id.slice(0, 8)})` : ""}`; }

  class BikeWeatherCard extends HTMLElement {
    constructor() { super(); this.config = {...DEFAULT_CONFIG}; this.data = null; this.loading = false; this.entryState = "loading"; this.error = null; }
    setConfig(config) { this.config = {...DEFAULT_CONFIG, ...(config || {})}; this.data = null; this.error = null; this.entryState = "loading"; this.render(); if (this._hass) this.refresh(); }
    set hass(value) { this._hass = value; if (this._lastConnection !== value?.connection) { this._lastConnection = value?.connection; this.refresh(); } }
    async refresh() {
      if (!this._hass || !this.config) return;
      this.loading = true; this.error = null; this.entryState = "loading"; this.render();
      let entries = null;
      try { entries = (await this._hass.callWS({type:LIST_ENTRIES})).entries || []; }
      catch (err) { if (!this.config.entry_id) { this.error = strings(this._hass).entryError; this.entryState = "error"; this.loading = false; this.render(); return; } }
      const t = strings(this._hass), available = (entries || []).filter((entry) => entry.available);
      let selected = this.config.entry_id ? (entries || []).find((entry) => entry.entry_id === this.config.entry_id) : null;
      if (this.config.entry_id && entries && !selected) { this.error = t.invalidEntry; this.entryState = "invalid"; this.loading = false; this.render(); return; }
      if (selected && !selected.available) { this.error = t.entryUnavailable; this.entryState = "unavailable"; this.loading = false; this.render(); return; }
      if (!selected && available.length === 1) selected = available[0];
      if (!selected) { this.entryState = available.length ? "choose" : "none"; this.loading = false; this.render(); return; }
      this.entryState = "selected";
      try { this.data = await this._hass.callWS({type:CARD_DATA, entry_id:selected.entry_id}); this.error = null; }
      catch (err) { this.error = t.connectionError; }
      this.loading = false; this.render();
    }
    render() {
      if (!this.shadowRoot) this.attachShadow({mode:"open"});
      const t = strings(this._hass), d = this.data, c = d && d.current || {}, forecast = (d && d.forecast || []).slice(0, 6);
      const status = d ? `${translatedStatus(d.assessment, t)} · ${d.score == null ? "—" : d.score}/100` : (this.loading ? t.loading : t.unavailable);
      const stale = !d || d.quality === "stale" || d.quality === "unavailable";
      const errors = (d && d.errors || []).map((error) => translatedError(error, t)).join(", ");
      const source = (d && d.sources || []).map((item) => translatedSource(item, t)).join(", ") || "—";
      let notice = this.error || (this.entryState === "none" ? t.noEntry : this.entryState === "choose" ? t.chooseEntry : this.entryState === "loading" && !d ? t.entryLoading : "");
      this.shadowRoot.innerHTML = `<style>:host{display:block;contain:content}.card{padding:16px;border-radius:14px;background:var(--ha-card-background,var(--card-background-color,#fff));color:var(--primary-text-color);box-shadow:var(--ha-card-box-shadow,none);overflow:hidden}.header{display:flex;justify-content:space-between;gap:12px;align-items:center}.title{font-size:1.15em;font-weight:600}.status{color:var(--secondary-text-color);margin-top:4px}.score{font-size:2em;font-weight:700;color:var(--primary-color)}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:14px}.metric,.slot{padding:10px;background:var(--secondary-background-color,#eee);border-radius:10px;min-width:0}.label{font-size:.78em;color:var(--secondary-text-color);overflow-wrap:anywhere}.value{margin-top:3px;font-weight:600}.forecast{display:grid;grid-template-columns:repeat(auto-fit,minmax(72px,1fr));gap:8px;margin-top:8px}.error{color:var(--error-color,#db4437);overflow-wrap:anywhere}.notice{color:var(--warning-color,#a66b00);margin:12px 0 0}.meta{margin-top:12px;font-size:.82em;color:var(--secondary-text-color);overflow-wrap:anywhere}@media(max-width:420px){.card{padding:12px}.grid{gap:6px}.metric{padding:8px}.score{font-size:1.65em}}</style><ha-card class="card"><div class="header"><div><div class="title">${esc(t.title)}</div><div class="status">${esc(status)}</div></div><div class="score">${d && d.score != null ? esc(d.score) : "—"}</div></div>${notice ? `<p class="${this.error ? "error" : "notice"}">${esc(notice)}</p>` : ""}${errors ? `<p class="error">${esc(errors)}</p>` : ""}${stale && !this.error && d ? `<p class="notice">${esc(t.stale)}</p>` : ""}<div class="grid"><div class="metric"><div class="label">${esc(t.temperature)}</div><div class="value">${value(c.temperature_c,"°C")}</div></div><div class="metric"><div class="label">${esc(t.wind)}</div><div class="value">${value(c.wind_kmh,"km/h")}</div></div><div class="metric"><div class="label">${esc(t.rain)}</div><div class="value">${value(c.precipitation_mm,"mm/h")}</div></div></div>${this.config.show_forecast ? `<div class="label" style="margin-top:14px">${esc(t.forecast)}</div><div class="forecast">${forecast.map((slot) => `<div class="slot"><div class="label">${time(slot.datetime)}</div><div class="value">${slot.score == null ? "—" : esc(slot.score)}</div><div class="label">${esc(translatedStatus(slot.status, t))}</div></div>`).join("") || `<div class="label">${esc(t.noForecast)}</div>`}</div>` : ""}${this.config.show_details && d ? `<div class="meta">${esc(t.window)}: ${esc(this.config.ride_start)} · ${esc(this.config.ride_duration_minutes)} ${esc(t.minutes)}<br>${esc(t.source)}: ${esc(source)} · ${esc(t.quality)}: ${esc(translatedQuality(d.quality, t))}</div>` : ""}</ha-card>`;
    }
    getCardSize() { return 4; }
    static getConfigElement() { return document.createElement("bike-weather-card-editor"); }
    static getStubConfig() { return {...DEFAULT_CONFIG}; }
  }

  class BikeWeatherCardEditor extends HTMLElement {
    constructor() { super(); this.config = {...DEFAULT_CONFIG}; this.entries = []; this.entryState = "loading"; }
    setConfig(config) { this.config = {...DEFAULT_CONFIG, ...(config || {})}; this.render(); if (this._hass) this.loadEntries(); }
    set hass(value) { this._hass = value; if (this._lastConnection !== value?.connection) { this._lastConnection = value?.connection; this.loadEntries(); } this.render(); }
    async loadEntries() {
      if (!this._hass) return;
      this.entryState = "loading"; this.render();
      try { this.entries = (await this._hass.callWS({type:LIST_ENTRIES})).entries || []; this.entryState = "ready"; }
      catch (err) { this.entries = []; this.entryState = "error"; }
      this.render();
    }
    emitConfig() { this.dispatchEvent(new CustomEvent("config-changed", {bubbles:true, composed:true, detail:{config:{...this.config}}})); }
    render() {
      if (!this.config) return;
      const t = strings(this._hass), counts = this.entries.reduce((all, entry) => { all[entry.title] = (all[entry.title] || 0) + 1; return all; }, {});
      const selectOptions = this.entryState === "loading" ? `<option value="">${esc(t.entryLoading)}</option>` : this.entries.length === 0 ? `<option value="">${esc(this.entryState === "error" ? t.entryError : t.noEntry)}</option>` : `${this.entries.length === 1 ? `<option value="">${esc(t.entryAuto)}</option>` : `<option value="">${esc(t.chooseEntry)}</option>`}${this.entries.map((entry) => `<option value="${esc(entry.entry_id)}" ${this.config.entry_id === entry.entry_id ? "selected" : ""} ${entry.available ? "" : "disabled"}>${esc(entryLabel(entry, counts))}${entry.available ? "" : ` — ${esc(t.entryUnavailable)}`}</option>`).join("")}`;
      this.innerHTML = `<style>:host{display:block;padding:8px}.row{display:block;margin:8px 0}input,select{width:100%;box-sizing:border-box;padding:6px}</style><label class="row">${esc(t.entry)}<select data-key="entry_id">${selectOptions}</select></label><label class="row">${esc(t.start)}<input data-key="ride_start" value="${esc(this.config.ride_start)}"></label><label class="row">${esc(t.duration)}<input type="number" min="1" max="1440" data-key="ride_duration_minutes" value="${esc(this.config.ride_duration_minutes)}"></label><label class="row"><input type="checkbox" data-key="show_forecast" ${this.config.show_forecast ? "checked" : ""}> ${esc(t.showForecast)}</label><label class="row"><input type="checkbox" data-key="show_details" ${this.config.show_details ? "checked" : ""}> ${esc(t.showDetails)}</label>`;
      this.querySelectorAll("[data-key]").forEach((el) => el.addEventListener("change", () => { const key = el.dataset.key; if (key === "entry_id") { if (el.value) this.config.entry_id = el.value; else delete this.config.entry_id; } else this.config[key] = el.type === "checkbox" ? el.checked : (el.type === "number" ? Number(el.value) : el.value); this.emitConfig(); }));
    }
  }
  if (!customElements.get("bike-weather-card")) customElements.define("bike-weather-card", BikeWeatherCard);
  if (!customElements.get("bike-weather-card-editor")) customElements.define("bike-weather-card-editor", BikeWeatherCardEditor);
  window.BIKE_WEATHER_CARD_VERSION = VERSION;
})();
