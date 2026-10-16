import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

class FakeElement {
  constructor() { this.listeners = {}; this.controls = []; this._innerHTML = ""; }
  attachShadow() { this.shadowRoot = {innerHTML: ""}; return this.shadowRoot; }
  set innerHTML(value) {
    this._innerHTML = value;
    this.controls = [...value.matchAll(/data-key="([^"]+)"/g)].map((match) => ({
      dataset: {key: match[1]}, type: match[1] === "show_forecast" || match[1] === "show_details" ? "checkbox" : match[1] === "ride_duration_minutes" ? "number" : match[1] === "entry_id" ? "select-one" : "text",
      value: "",
      checked: false,
      listeners: {},
      addEventListener(type, fn) { this.listeners[type] = fn; },
      dispatchEvent(event) { this.listeners[event.type]?.(event); }
    }));
  }
  get innerHTML() { return this._innerHTML; }
  querySelectorAll() { return this.controls; }
  addEventListener(type, fn) { this.listeners[type] = fn; }
  dispatchEvent(event) { this.listeners[event.type]?.(event); }
}

const registry = new Map();
globalThis.window = {customCards: []};
globalThis.HTMLElement = FakeElement;
globalThis.customElements = {get: (name) => registry.get(name), define: (name, value) => registry.set(name, value)};
globalThis.document = {createElement: (name) => { const Element = registry.get(name); return Element ? new Element() : new FakeElement(); }};
globalThis.CustomEvent = class { constructor(type, init) { this.type = type; Object.assign(this, init?.detail || {}); } };
vm.runInThisContext(fs.readFileSync("custom_components/bike_weather/www/bike-weather-card.js", "utf8"));
const cardSource = fs.readFileSync("custom_components/bike_weather/www/bike-weather-card.js", "utf8");
assert.match(cardSource, /spontaneous_ride_storage_key/);
assert.match(cardSource, /_dashboardInstanceKey/);
assert.doesNotMatch(cardSource, /class="forecast"/);
assert.doesNotMatch(cardSource, /const forecast/);

const data = {assessment: "good", score: 88, quality: "good", sources: ["ha_weather"], errors: [], current: {temperature_c: 18, wind_kmh: 4, precipitation_mm: 0}, forecast: []};
const wait = () => new Promise((resolve) => setTimeout(resolve, 0));
const makeHass = (entries, payload = {}) => {
  const calls = [];
  return {hass: {connection: {}, locale: {language: "en"}, callWS: async (message) => { calls.push(message); return message.type === "bike_weather/list_entries" ? {entries} : payload[message.type] || data; }}, calls};
};

{
  const planning = {rides: {outbound: {name: "Outbound", status: "good", score: 80, start_time: "07:30", duration_minutes: 30, metrics: {temperature_c: 18, wind_kmh: 4, maximum_gust_kmh: 8}}, return: {name: "Return", status: "good", score: 75, start_time: "13:30", duration_minutes: 30, metrics: {temperature_c: 20, wind_kmh: 5, maximum_gust_kmh: 9}}}, tomorrow: {date: "2026-10-17", status: "good", score: 82, quality: "good", metrics: {minimum_temperature_c: 12, maximum_temperature_c: 20, maximum_wind_kmh: 10, precipitation_probability_pct: 10}, suitable_windows: [], adverse_windows: []}};
  const ride = {status: "good", score: 84, quality: "good", start_at: "2026-10-16T13:30:00Z", end_at: "2026-10-16T14:30:00Z", forecast_coverage: {complete: true}, metrics: {temperature_c: 18, wind_kmh: 4, maximum_gust_kmh: 8, precipitation_mm: 0, precipitation_probability_pct: 10}, reason_codes: ["good_conditions"]};
  const populatedData = {...data, forecast: [{datetime: "2026-10-16T13:00:00Z", score: 80, status: "good"}, {datetime: "2026-10-16T14:00:00Z", score: 81, status: "good"}]};
  const {hass, calls} = makeHass([{entry_id: "one", title: "Garden", state: "loaded", available: true}], {"bike_weather/card_data": populatedData, "bike_weather/planning_data": planning, "bike_weather/spontaneous_ride": ride});
  hass.locale.language = "de";
  const card = new (customElements.get("bike-weather-card"))();
  card.setConfig({ride_datetime: "2026-10-16T13:30"});
  card.hass = hass;
  await wait();
  assert.deepEqual(calls.map((item) => item.type), ["bike_weather/list_entries", "bike_weather/card_data", "bike_weather/planning_data", "bike_weather/spontaneous_ride"]);
  assert.equal(calls[3].start_at, "2026-10-16T13:30");
  assert.match(card.shadowRoot.innerHTML, /88/);
  assert.doesNotMatch(card.shadowRoot.innerHTML, /class="forecast"/);
  assert.doesNotMatch(card.shadowRoot.innerHTML, /class="slot"/);
  assert.ok(card.shadowRoot.innerHTML.includes("Heute – Meine Fahrten"));
  assert.ok(card.shadowRoot.innerHTML.includes("Morgen – Fahrradwetter"));
  assert.ok(card.shadowRoot.innerHTML.includes("Spontane Fahrradtour"));
  assert.ok(card.shadowRoot.innerHTML.indexOf("Heute – Meine Fahrten") < card.shadowRoot.innerHTML.indexOf("Morgen – Fahrradwetter"));
  assert.ok(card.shadowRoot.innerHTML.indexOf("Morgen – Fahrradwetter") < card.shadowRoot.innerHTML.indexOf("Spontane Fahrradtour"));
  assert.doesNotMatch(card.shadowRoot.innerHTML, /Ride window:/);
}

{
  const {hass, calls} = makeHass([
    {entry_id: "one", title: "Garden", state: "loaded", available: true},
    {entry_id: "two", title: "Balcony", state: "loaded", available: true}
  ]);
  const card = new (customElements.get("bike-weather-card"))();
  card.setConfig({});
  card.hass = hass;
  await wait();
  assert.deepEqual(calls.map((item) => item.type), ["bike_weather/list_entries"]);
  assert.match(card.shadowRoot.innerHTML, /Multiple Bike Weather integrations/);
}

{
  const {hass} = makeHass([{entry_id: "one", title: "Garden", state: "loaded", available: true}, {entry_id: "two", title: "Balcony", state: "loaded", available: true}]);
  const editor = new (customElements.get("bike-weather-card-editor"))();
  let changed;
  editor.addEventListener("config-changed", (event) => { changed = event.config; });
  editor.setConfig({});
  editor.hass = hass;
  await wait();
  const select = editor.querySelectorAll().find((control) => control.dataset.key === "entry_id");
  select.value = "two";
  select.dispatchEvent({type: "change"});
  assert.equal(changed.entry_id, "two");
}

{
  const {hass, calls} = makeHass([]);
  const card = new (customElements.get("bike-weather-card"))();
  card.setConfig({});
  card.hass = hass;
  await wait();
  assert.deepEqual(calls.map((item) => item.type), ["bike_weather/list_entries"]);
  assert.match(card.shadowRoot.innerHTML, /No Bike Weather integration/);
}

{
  const {hass, calls} = makeHass([{entry_id: "one", title: "Garden", state: "loaded", available: true}]);
  const card = new (customElements.get("bike-weather-card"))();
  card.setConfig({entry_id: "deleted"});
  card.hass = hass;
  await wait();
  assert.deepEqual(calls.map((item) => item.type), ["bike_weather/list_entries"]);
  assert.match(card.shadowRoot.innerHTML, /configured Bike Weather integration was not found/);
}

{
  const {hass, calls} = makeHass([{entry_id: "one", title: "Garden", state: "loaded", available: true}, {entry_id: "two", title: "Balcony", state: "loaded", available: true}]);
  const card = new (customElements.get("bike-weather-card"))();
  card.setConfig({entry_id: "two"});
  card.hass = hass;
  await wait();
  assert.deepEqual(calls.map((item) => item.type), ["bike_weather/list_entries", "bike_weather/card_data", "bike_weather/planning_data", "bike_weather/spontaneous_ride"]);
  assert.equal(calls[1].entry_id, "two");
}

{
  const {hass} = makeHass([]);
  hass.locale.language = "de";
  const editor = new (customElements.get("bike-weather-card-editor"))();
  editor.hass = hass;
  await wait();
  assert.match(editor.innerHTML, /Keine Bike-Weather-Integration/);
}

console.log("Phase 9D card interaction tests passed");
