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

const data = {assessment: "good", score: 88, quality: "good", sources: ["ha_weather"], errors: [], current: {temperature_c: 18, wind_kmh: 4, precipitation_mm: 0}, forecast: []};
const wait = () => new Promise((resolve) => setTimeout(resolve, 0));
const makeHass = (entries) => {
  const calls = [];
  return {hass: {connection: {}, locale: {language: "en"}, callWS: async (message) => { calls.push(message); return message.type === "bike_weather/list_entries" ? {entries} : data; }}, calls};
};

{
  const {hass, calls} = makeHass([{entry_id: "one", title: "Garden", state: "loaded", available: true}]);
  const card = new (customElements.get("bike-weather-card"))();
  card.setConfig({});
  card.hass = hass;
  await wait();
  assert.deepEqual(calls.map((item) => item.type), ["bike_weather/list_entries", "bike_weather/card_data", "bike_weather/spontaneous_ride"]);
  assert.match(card.shadowRoot.innerHTML, /88/);
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
  assert.deepEqual(calls.map((item) => item.type), ["bike_weather/list_entries", "bike_weather/card_data", "bike_weather/spontaneous_ride"]);
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
