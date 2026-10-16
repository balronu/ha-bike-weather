/* Bike Weather card v0.2.0-beta.1. */
(function () {
  "use strict";
  const VERSION = "0.2.0-beta.1";
  const LIST_ENTRIES = "bike_weather/list_entries";
  const CARD_DATA = "bike_weather/card_data";
  const RIDE_DATA = "bike_weather/spontaneous_ride";
  const DURATIONS = [15, 30, 45, 60, 90, 120];
  const DEFAULT_CONFIG = {show_forecast:true, show_details:true, ride_start:"15:00", ride_duration_minutes:60};
  const registered = window.customCards || (window.customCards = []);
  if (!registered.some((card) => card.type === "bike-weather-card")) registered.push({type:"bike-weather-card", name:"Bike Weather", description:"Cycling weather score and forecast"});
  const TEXT = {
    de: {title:"Fahrradwetter",loading:"Lade…",unavailable:"Nicht verfügbar",connectionError:"Kartendaten konnten nicht geladen werden",temperature:"Temperatur",wind:"Wind",gust:"Windböen",rain:"Regen",probability:"Regenwahrscheinlichkeit",forecast:"Prognose",source:"Quelle",quality:"Datenqualität",noForecast:"Keine Prognosedaten",window:"Fahrzeitfenster",duration:"Fahrtdauer",minutes:"Minuten",stale:"Daten fehlen oder sind veraltet",unknown:"unbekannt",good:"geeignet",bad:"nicht geeignet",partial:"eingeschränkt",staleQuality:"veraltet",unavailableQuality:"nicht verfügbar",invalid:"ungültig",local:"Lokale Wetterstation",ha_weather:"Home-Assistant-Wetter",openweathermap:"OpenWeatherMap",providerError:"Wetteranbieter nicht erreichbar",weatherUnavailable:"Home-Assistant-Wetterdaten nicht verfügbar",invalidEntry:"Die konfigurierte Bike-Weather-Integration wurde nicht gefunden.",noEntry:"Keine Bike-Weather-Integration verfügbar.",chooseEntry:"Mehrere Bike-Weather-Integrationen gefunden. Bitte eine auswählen.",entryLoading:"Bike-Weather-Integrationen werden geladen…",entryAuto:"Automatisch erkannte Integration",entryUnavailable:"Integration nicht geladen",entryError:"Integrationen konnten nicht ermittelt werden",entry:"Bike-Weather-Eintrag",showForecast:"Prognose anzeigen",showDetails:"Details anzeigen",start:"Abfahrt",spontaneous:"Spontane Fahrradtour",arrival:"Ankunft",calculate:"Berechne…",rideError:"Fahrtbewertung konnte nicht geladen werden",coverage:"Prognoseabdeckung",incomplete:"Für das gesamte Zeitfenster liegen nicht genügend Prognosedaten vor.",good_conditions:"Gute Bedingungen für die gesamte Fahrt.",rain_during_ride:"Während der Fahrt ist Regen möglich.",rain_possible:"Während der Fahrt ist Regen möglich.",temperature_below_limit:"Die Temperatur liegt unter deiner eingestellten Mindesttemperatur.",wind_above_limit:"Die Windgeschwindigkeit überschreitet deinen Grenzwert.",gust_above_limit:"Relevante Windböen überschreiten deinen Grenzwert.",forecast_stale:"Die Prognosedaten sind veraltet.",forecast_unavailable:"Für das gewählte Zeitfenster liegen keine Prognosedaten vor.",start_in_past:"Die Abfahrt muss in der Zukunft liegen.",invalid_start:"Bitte ein gültiges Datum und eine gültige Uhrzeit wählen."},
    en: {title:"Bike Weather",loading:"Loading…",unavailable:"Unavailable",connectionError:"Card data could not be loaded",temperature:"Temperature",wind:"Wind",gust:"Gusts",rain:"Rain",probability:"Rain probability",forecast:"Forecast",source:"Source",quality:"Data quality",noForecast:"No forecast data",window:"Ride window",duration:"Ride duration",minutes:"minutes",stale:"Data missing or stale",unknown:"unknown",good:"suitable",bad:"not suitable",partial:"limited",staleQuality:"stale",unavailableQuality:"unavailable",invalid:"invalid",local:"Local weather station",ha_weather:"Home Assistant weather",openweathermap:"OpenWeatherMap",providerError:"Weather provider unavailable",weatherUnavailable:"Home Assistant weather data unavailable",invalidEntry:"The configured Bike Weather integration was not found.",noEntry:"No Bike Weather integration is available.",chooseEntry:"Multiple Bike Weather integrations were found. Select one.",entryLoading:"Loading Bike Weather integrations…",entryAuto:"Automatically detected integration",entryUnavailable:"Integration is not loaded",entryError:"Integrations could not be loaded",entry:"Bike Weather entry",showForecast:"Show forecast",showDetails:"Show details",start:"Departure",spontaneous:"Spontaneous bike ride",arrival:"Arrival",calculate:"Calculating…",rideError:"Ride assessment could not be loaded",coverage:"Forecast coverage",incomplete:"There is not enough forecast data for the entire ride window.",good_conditions:"Good conditions for the entire ride.",rain_during_ride:"Rain is possible during the ride.",rain_possible:"Rain is possible during the ride.",temperature_below_limit:"The temperature is below your configured minimum.",wind_above_limit:"Wind speed exceeds your configured limit.",gust_above_limit:"Relevant gusts exceed your configured limit.",forecast_stale:"Forecast data is stale.",forecast_unavailable:"No forecast data is available for the selected window.",start_in_past:"Departure must be in the future.",invalid_start:"Please choose a valid date and time."}
  };
  function strings(hass) { return (hass && hass.locale && hass.locale.language || "en").startsWith("de") ? TEXT.de : TEXT.en; }
  function translatedStatus(status, t) { return t[status] || t.unknown; }
  function translatedQuality(quality, t) { return ({good:t.good, partial:t.partial, stale:t.staleQuality, unavailable:t.unavailableQuality, invalid:t.invalid}[quality]) || t.unknown; }
  function translatedSource(source, t) { return t[source] || t.unknown; }
  function translatedError(error, t) { return ({provider_error:t.providerError, ha_weather_unavailable:t.weatherUnavailable, ha_forecast_unavailable:t.noForecast}[error]) || t.unknown; }
  function esc(v) { return String(v == null ? "" : v).replace(/[&<>"']/g, (x) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[x])); }
  function value(v, unit) { return v == null ? "—" : `${Number(v).toFixed(1)} ${unit}`; }
  function time(v) { if (!v) return "—"; const d = new Date(v); return Number.isNaN(d.valueOf()) ? "—" : d.toLocaleTimeString([], {hour:"2-digit", minute:"2-digit"}); }
  function dateTime(v) { if (!v) return "—"; const d = new Date(v); return Number.isNaN(d.valueOf()) ? "—" : d.toLocaleString([], {dateStyle:"medium", timeStyle:"short"}); }
  function entryLabel(entry, duplicates) { return `${entry.title || "Bike Weather"}${duplicates[entry.title] > 1 ? ` (${entry.entry_id.slice(0, 8)})` : ""}`; }
  function localDateTime(hass) {
    const zone = hass?.config?.time_zone;
    const parts = new Intl.DateTimeFormat("en-CA", {timeZone:zone, year:"numeric", month:"2-digit", day:"2-digit", hour:"2-digit", minute:"2-digit", hourCycle:"h23"}).formatToParts(new Date());
    const get = (name) => parts.find((part) => part.type === name)?.value;
    let value = `${get("year")}-${get("month")}-${get("day")}T15:00`;
    const now = `${get("year")}-${get("month")}-${get("day")}T${get("hour")}:${get("minute")}`;
    if (now >= value) { const d = new Date(`${get("year")}-${get("month")}-${get("day")}T12:00:00Z`); d.setUTCDate(d.getUTCDate() + 1); value = `${d.getUTCFullYear()}-${String(d.getUTCMonth()+1).padStart(2,"0")}-${String(d.getUTCDate()).padStart(2,"0")}T15:00`; }
    return value;
  }
  function storageKey(config, entryId) { return `bike-weather:spontaneous:${config.spontaneous_ride_storage_key || entryId || "auto"}`; }
  function readRide(config, hass, entryId) {
    let saved = null;
    try { saved = JSON.parse(localStorage.getItem(storageKey(config, entryId)) || "null"); } catch (_) {}
    const start = saved?.start_at || config.ride_datetime || localDateTime(hass);
    const legacy = config.ride_start && /^\d{2}:\d{2}$/.test(config.ride_start);
    return {start_at: legacy && !saved && !config.ride_datetime ? `${localDateTime(hass).slice(0,10)}T${config.ride_start}` : start, duration_minutes: Number(saved?.duration_minutes || config.ride_duration_minutes || 60)};
  }
  function saveRide(config, entryId, ride) { try { localStorage.setItem(storageKey(config, entryId), JSON.stringify(ride)); } catch (_) {} }

  class BikeWeatherCard extends HTMLElement {
    constructor() { super(); this.config = {...DEFAULT_CONFIG}; this.data = null; this.rideData = null; this.loading = false; this.rideLoading = false; this.entryState = "loading"; this.error = null; this.rideError = null; this.ride = null; this._rideTimer = null; this._saveTimer = null; }
    setConfig(config) { this.config = {...DEFAULT_CONFIG, ...(config || {})}; this.data = null; this.rideData = null; this.error = null; this.entryState = "loading"; this.render(); if (this._hass) this.refresh(); }
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
      this.entryState = "selected"; this.ride = readRide(this.config, this._hass, selected.entry_id);
      try { this.data = await this._hass.callWS({type:CARD_DATA, entry_id:selected.entry_id}); this.error = null; await this.refreshRide(selected.entry_id); }
      catch (err) { this.error = t.connectionError; }
      this.loading = false; this.render();
    }
    scheduleRide(entryId) { clearTimeout(this._rideTimer); this._rideTimer = setTimeout(() => this.refreshRide(entryId), 350); clearTimeout(this._saveTimer); this._saveTimer = setTimeout(() => saveRide(this.config, entryId, this.ride), 500); }
    async refreshRide(entryId) {
      if (!this._hass || !this.ride || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(this.ride.start_at) || !DURATIONS.includes(Number(this.ride.duration_minutes))) { this.rideError = strings(this._hass).invalid_start; this.render(); return; }
      this.rideLoading = true; this.rideError = null; this.render();
      try { this.rideData = await this._hass.callWS({type:RIDE_DATA, entry_id:entryId, start_at:this.ride.start_at, duration_minutes:Number(this.ride.duration_minutes), timezone:this._hass.config?.time_zone}); }
      catch (err) { this.rideData = null; this.rideError = strings(this._hass).rideError; }
      this.rideLoading = false; this.render();
    }
    changeRide(entryId, key, value) { this.ride = {...this.ride, [key]: key === "duration_minutes" ? Number(value) : value}; this.rideData = null; this.scheduleRide(entryId); this.render(); }
    render() {
      if (!this.shadowRoot) this.attachShadow({mode:"open"});
      const t = strings(this._hass), d = this.data, c = d && d.current || {}, r = this.rideData, forecast = (d && d.forecast || []).slice(0, 6), m = r && r.metrics || {};
      const status = d ? `${translatedStatus(d.assessment, t)} · ${d.score == null ? "—" : d.score}/100` : (this.loading ? t.loading : t.unavailable);
      const stale = !d || d.quality === "stale" || d.quality === "unavailable";
      const errors = (d && d.errors || []).map((error) => translatedError(error, t)).join(", ");
      const source = (d && d.sources || []).map((item) => translatedSource(item, t)).join(", ") || "—";
      const notice = this.error || (this.entryState === "none" ? t.noEntry : this.entryState === "choose" ? t.chooseEntry : this.entryState === "loading" && !d ? t.entryLoading : "");
      const rideReasons = (r?.reason_codes || []).map((code) => t[code] || code);
      const rideScore = r?.score == null ? "—" : `${r.score}/100`;
      const rideStatus = r ? translatedStatus(r.status, t) : (this.rideLoading ? t.calculate : "—");
      const rideStart = this.ride?.start_at || "";
      this.shadowRoot.innerHTML = `<style>:host{display:block;contain:content}.card{padding:16px;border-radius:14px;background:var(--ha-card-background,var(--card-background-color,#fff));color:var(--primary-text-color);box-shadow:var(--ha-card-box-shadow,none);overflow:hidden}.header{display:flex;justify-content:space-between;gap:12px;align-items:center}.title{font-size:1.15em;font-weight:600}.status{color:var(--secondary-text-color);margin-top:4px}.score{font-size:2em;font-weight:700;color:var(--primary-color)}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:14px}.metric,.slot{padding:10px;background:var(--secondary-background-color,#eee);border-radius:10px;min-width:0}.label{font-size:.78em;color:var(--secondary-text-color);overflow-wrap:anywhere}.value{margin-top:3px;font-weight:600}.forecast{display:grid;grid-template-columns:repeat(auto-fit,minmax(72px,1fr));gap:8px;margin-top:8px}.error{color:var(--error-color,#db4437);overflow-wrap:anywhere}.notice{color:var(--warning-color,#a66b00);margin:12px 0 0}.meta{margin-top:12px;font-size:.82em;color:var(--secondary-text-color);overflow-wrap:anywhere}.ride{margin-top:16px;padding-top:14px;border-top:1px solid var(--divider-color,#ddd)}.ride h3{margin:0 0 10px}.ride-controls{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(110px,.8fr);gap:8px}.ride input,.ride select{width:100%;box-sizing:border-box;padding:8px;border:1px solid var(--divider-color,#aaa);border-radius:8px;background:var(--card-background-color,#fff);color:inherit}.ride-result{margin-top:12px}.ride-score{font-size:1.5em;font-weight:700;color:var(--primary-color)}.ride-reasons{margin:8px 0 0;padding-left:18px}.ride-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px;margin-top:8px}@media(max-width:420px){.card{padding:12px}.grid,.ride-metrics{gap:6px}.metric{padding:8px}.score{font-size:1.65em}.ride-controls{grid-template-columns:1fr}.ride-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}}</style><ha-card class="card"><div class="header"><div><div class="title">${esc(t.title)}</div><div class="status">${esc(status)}</div></div><div class="score">${d && d.score != null ? esc(d.score) : "—"}</div></div>${notice ? `<p class="${this.error ? "error" : "notice"}">${esc(notice)}</p>` : ""}${errors ? `<p class="error">${esc(errors)}</p>` : ""}${stale && !this.error && d ? `<p class="notice">${esc(t.stale)}</p>` : ""}<div class="grid"><div class="metric"><div class="label">${esc(t.temperature)}</div><div class="value">${value(c.temperature_c,"°C")}</div></div><div class="metric"><div class="label">${esc(t.wind)}</div><div class="value">${value(c.wind_kmh,"km/h")}</div></div><div class="metric"><div class="label">${esc(t.rain)}</div><div class="value">${value(c.precipitation_mm,"mm/h")}</div></div></div>${this.config.show_forecast ? `<div class="label" style="margin-top:14px">${esc(t.forecast)}</div><div class="forecast">${forecast.map((slot) => `<div class="slot"><div class="label">${time(slot.datetime)}</div><div class="value">${slot.score == null ? "—" : esc(slot.score)}</div><div class="label">${esc(translatedStatus(slot.status, t))}</div></div>`).join("") || `<div class="label">${esc(t.noForecast)}</div>`}</div>` : ""}<section class="ride"><h3>${esc(t.spontaneous)}</h3><div class="ride-controls"><label class="label">${esc(t.start)}<input data-ride="start_at" type="datetime-local" value="${esc(rideStart)}"></label><label class="label">${esc(t.duration)}<select data-ride="duration_minutes">${DURATIONS.map((minutes) => `<option value="${minutes}" ${Number(this.ride?.duration_minutes) === minutes ? "selected" : ""}>${minutes} ${esc(t.minutes)}</option>`).join("")}</select></label></div><div class="ride-result">${this.rideLoading ? `<p class="notice">${esc(t.calculate)}</p>` : r ? `<div class="ride-score">${esc(rideStatus)} · ${esc(rideScore)}</div><div class="meta">${esc(t.start)}: ${esc(dateTime(r.start_at))} · ${esc(t.arrival)}: ${esc(dateTime(r.end_at))}<br>${esc(t.quality)}: ${esc(translatedQuality(r.quality,t))}${r.forecast_coverage?.complete ? "" : ` · ${esc(t.coverage)}: ${esc(t.incomplete)}`}</div><div class="ride-metrics"><div class="metric"><div class="label">${esc(t.temperature)}</div><div class="value">${value(m.temperature_c,"°C")}</div></div><div class="metric"><div class="label">${esc(t.wind)}</div><div class="value">${value(m.wind_kmh,"km/h")}</div></div><div class="metric"><div class="label">${esc(t.gust)}</div><div class="value">${value(m.maximum_gust_kmh,"km/h")}</div></div><div class="metric"><div class="label">${esc(t.rain)}</div><div class="value">${value(m.precipitation_mm,"mm")}</div></div><div class="metric"><div class="label">${esc(t.probability)}</div><div class="value">${value(m.precipitation_probability_pct,"%")}</div></div></div><ul class="ride-reasons">${rideReasons.map((reason) => `<li>${esc(reason)}</li>`).join("")}</ul>` : this.rideError ? `<p class="error">${esc(this.rideError)}</p>` : ""}</div></section>${this.config.show_details && d ? `<div class="meta">${esc(t.window)}: ${esc(this.config.ride_start || "15:00")} · ${esc(this.config.ride_duration_minutes || 60)} ${esc(t.minutes)}<br>${esc(t.source)}: ${esc(source)} · ${esc(t.quality)}: ${esc(translatedQuality(d.quality, t))}</div>` : ""}</ha-card>`;
      (this.shadowRoot.querySelectorAll ? this.shadowRoot.querySelectorAll("[data-ride]") : []).forEach((el) => el.addEventListener("change", () => { const entryId = d?.entry_id; if (!entryId) return; this.changeRide(entryId, el.dataset.ride, el.value); }));
    }
    getCardSize() { return 6; }
    static getConfigElement() { return document.createElement("bike-weather-card-editor"); }
    static getStubConfig() { return {...DEFAULT_CONFIG}; }
  }

  class BikeWeatherCardEditor extends HTMLElement {
    constructor() { super(); this.config = {...DEFAULT_CONFIG}; this.entries = []; this.entryState = "loading"; }
    setConfig(config) { this.config = {...DEFAULT_CONFIG, ...(config || {})}; this.render(); if (this._hass) this.loadEntries(); }
    set hass(value) { this._hass = value; if (this._lastConnection !== value?.connection) { this._lastConnection = value?.connection; this.loadEntries(); } this.render(); }
    async loadEntries() { if (!this._hass) return; this.entryState = "loading"; this.render(); try { this.entries = (await this._hass.callWS({type:LIST_ENTRIES})).entries || []; this.entryState = "ready"; } catch (err) { this.entries = []; this.entryState = "error"; } this.render(); }
    emitConfig() { this.dispatchEvent(new CustomEvent("config-changed", {bubbles:true, composed:true, detail:{config:{...this.config}}})); }
    render() {
      if (!this.config) return;
      const t = strings(this._hass), counts = this.entries.reduce((all, entry) => { all[entry.title] = (all[entry.title] || 0) + 1; return all; }, {});
      const selectOptions = this.entryState === "loading" ? `<option value="">${esc(t.entryLoading)}</option>` : this.entries.length === 0 ? `<option value="">${esc(this.entryState === "error" ? t.entryError : t.noEntry)}</option>` : `${this.entries.length === 1 ? `<option value="">${esc(t.entryAuto)}</option>` : `<option value="">${esc(t.chooseEntry)}</option>`}${this.entries.map((entry) => `<option value="${esc(entry.entry_id)}" ${this.config.entry_id === entry.entry_id ? "selected" : ""} ${entry.available ? "" : "disabled"}>${esc(entryLabel(entry, counts))}${entry.available ? "" : ` — ${esc(t.entryUnavailable)}`}</option>`).join("")}`;
      this.innerHTML = `<style>:host{display:block;padding:8px}.row{display:block;margin:8px 0}input,select{width:100%;box-sizing:border-box;padding:6px}</style><label class="row">${esc(t.entry)}<select data-key="entry_id">${selectOptions}</select></label><label class="row">${esc(t.start)}<input data-key="ride_start" type="time" value="${esc(this.config.ride_start)}"></label><label class="row">${esc(t.duration)}<select data-key="ride_duration_minutes">${DURATIONS.map((minutes) => `<option value="${minutes}" ${Number(this.config.ride_duration_minutes) === minutes ? "selected" : ""}>${minutes} ${esc(t.minutes)}</option>`).join("")}</select></label><label class="row"><input type="checkbox" data-key="show_forecast" ${this.config.show_forecast ? "checked" : ""}> ${esc(t.showForecast)}</label><label class="row"><input type="checkbox" data-key="show_details" ${this.config.show_details ? "checked" : ""}> ${esc(t.showDetails)}</label>`;
      this.querySelectorAll("[data-key]").forEach((el) => el.addEventListener("change", () => { const key = el.dataset.key; if (key === "entry_id") { if (el.value) this.config.entry_id = el.value; else delete this.config.entry_id; } else this.config[key] = el.type === "checkbox" ? el.checked : (key === "ride_duration_minutes" ? Number(el.value) : el.value); this.emitConfig(); }));
    }
  }
  if (!customElements.get("bike-weather-card")) customElements.define("bike-weather-card", BikeWeatherCard);
  if (!customElements.get("bike-weather-card-editor")) customElements.define("bike-weather-card-editor", BikeWeatherCardEditor);
  window.BIKE_WEATHER_CARD_VERSION = VERSION;
})();
