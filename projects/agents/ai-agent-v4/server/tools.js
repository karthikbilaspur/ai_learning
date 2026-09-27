import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { z } from "zod";
import { evaluate } from "mathjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dataPath = (file) => path.join(__dirname, "..", "data", file);

const employees = JSON.parse(await fs.readFile(dataPath("employees.json"), "utf8"));
const products = JSON.parse(await fs.readFile(dataPath("products.json"), "utf8"));
const calendar = JSON.parse(await fs.readFile(dataPath("calendar.json"), "utf8"));

// New in v4: tasks persist to data/tasks.json instead of living only in a
// runtime array, so they survive a server restart.
let tasks = [];
try {
  tasks = JSON.parse(await fs.readFile(dataPath("tasks.json"), "utf8"));
} catch {
  tasks = [];
}
async function saveTasks() {
  await fs.writeFile(dataPath("tasks.json"), JSON.stringify(tasks, null, 2), "utf8");
}

// New in v4: tools in this set don't run immediately. The agent loop pauses
// and the frontend must show a confirm/reject prompt before they execute.
export const requiresConfirmation = new Set(["create_task"]);

const schemas = {
  calculate: z.object({ expression: z.string().min(1).max(200) }),
  search_dataset: z.object({ query: z.string().min(1).max(100) }),
  analyze_dataset: z.object({
    metric: z.enum(["count", "average_salary", "highest_salary", "lowest_salary"]),
    department: z.string().optional(),
  }),
  get_weather: z.object({ city: z.string().min(1).max(80) }),
  convert_currency: z.object({ amount: z.number(), from: z.string().length(3), to: z.string().length(3) }),
  get_time: z.object({ timezone: z.string().min(1).max(80) }),
  search_web: z.object({ query: z.string().min(1).max(120) }),
  lookup_products: z.object({ query: z.string().min(1).max(80), maxPrice: z.number().optional() }),
  calendar_check: z.object({ date: z.string().min(1), preferredTime: z.string().optional() }),
  create_task: z.object({
    title: z.string().min(1).max(200),
    priority: z.enum(["low", "medium", "high"]).default("medium"),
  }),
};

function def(name, description, properties, required = Object.keys(properties)) {
  return {
    type: "function",
    function: { name, description, parameters: { type: "object", properties, required, additionalProperties: false } },
  };
}

export const toolDefinitions = [
  def("calculate", "Perform arithmetic safely.", { expression: { type: "string" } }),
  def("search_dataset", "Search employee data by name, department, city, role, or salary.", { query: { type: "string" } }),
  def(
    "analyze_dataset",
    "Calculate employee statistics.",
    { metric: { type: "string", enum: ["count", "average_salary", "highest_salary", "lowest_salary"] }, department: { type: "string" } },
    ["metric"]
  ),
  def("get_weather", "Get live current weather from Open-Meteo.", { city: { type: "string" } }),
  def("convert_currency", "Convert money using live Frankfurter rates.", { amount: { type: "number" }, from: { type: "string" }, to: { type: "string" } }),
  def("get_time", "Get current local time for an IANA timezone.", { timezone: { type: "string" } }),
  def("search_web", "Search the web using DuckDuckGo Instant Answer.", { query: { type: "string" } }),
  def("lookup_products", "Search the product catalog.", { query: { type: "string" }, maxPrice: { type: "number" } }, ["query"]),
  def("calendar_check", "Check demo calendar availability.", { date: { type: "string" }, preferredTime: { type: "string" } }, ["date"]),
  def(
    "create_task",
    "Create a server-side task. This action requires user confirmation before it runs.",
    { title: { type: "string" }, priority: { type: "string", enum: ["low", "medium", "high"] } },
    ["title"]
  ),
];

// New in v4: outbound calls to third-party APIs now time out instead of
// hanging the whole agent round if Open-Meteo/Frankfurter/DuckDuckGo stall.
const FETCH_TIMEOUT_MS = 8000;

async function fetchWithTimeout(url, ms = FETCH_TIMEOUT_MS) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ms);
  try {
    const res = await fetch(url, { signal: controller.signal });
    return await res.json();
  } catch (e) {
    if (e.name === "AbortError") throw new Error("Request timed out");
    throw e;
  } finally {
    clearTimeout(timer);
  }
}

async function weather(city) {
  const g = await fetchWithTimeout(
    `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1&language=en&format=json`
  );
  if (!g.results?.length) throw new Error("City not found");
  const p = g.results[0];
  const d = await fetchWithTimeout(
    `https://api.open-meteo.com/v1/forecast?latitude=${p.latitude}&longitude=${p.longitude}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m`
  );
  return {
    city: p.name,
    country: p.country,
    temperatureC: d.current.temperature_2m,
    humidity: d.current.relative_humidity_2m,
    windKmh: d.current.wind_speed_10m,
    weatherCode: d.current.weather_code,
  };
}

async function currency(amount, from, to) {
  const d = await fetchWithTimeout(
    `https://api.frankfurter.app/latest?amount=${amount}&from=${from.toUpperCase()}&to=${to.toUpperCase()}`
  );
  return { amount, from: from.toUpperCase(), to: to.toUpperCase(), converted: d.rates?.[to.toUpperCase()], date: d.date };
}

async function webSearch(query) {
  const d = await fetchWithTimeout(`https://api.duckduckgo.com/?q=${encodeURIComponent(query)}&format=json&no_html=1`);
  return {
    abstract: d.AbstractText || null,
    source: d.AbstractSource || null,
    url: d.AbstractURL || null,
    relatedTopics: (d.RelatedTopics || []).slice(0, 5).map((x) => x.Text).filter(Boolean),
  };
}

export async function executeTool(name, raw) {
  const a = schemas[name]?.parse(raw);
  if (!a) throw new Error("Unknown tool");

  switch (name) {
    case "calculate": {
      // Fixed in v4: the v3 regex was a literal `/^[0-9+\\-*/%().\\s]+$/`.
      // Because `\\-` and `\\s` inside a regex *literal* mean "escaped
      // backslash" + a stray `-`/`s` character (not "escaped hyphen" /
      // whitespace shorthand), the whitelist accidentally also allowed a
      // literal backslash and the letter "s" through. This version does
      // what it looks like it does.
      if (!/^[0-9+\-*/%().\s]+$/.test(a.expression)) throw new Error("Only arithmetic is allowed");
      return { expression: a.expression, result: evaluate(a.expression) };
    }
    case "search_dataset": {
      const q = a.query.toLowerCase();
      return employees.filter((e) => Object.values(e).some((v) => String(v).toLowerCase().includes(q))).slice(0, 20);
    }
    case "analyze_dataset": {
      const rows = a.department ? employees.filter((e) => e.department.toLowerCase() === a.department.toLowerCase()) : employees;
      if (a.metric === "count") return { count: rows.length };
      if (!rows.length) return { error: "No matches" };
      const s = rows.map((e) => e.salary);
      if (a.metric === "average_salary") return { averageSalary: s.reduce((x, y) => x + y, 0) / s.length };
      return a.metric === "highest_salary"
        ? rows.reduce((x, y) => (x.salary > y.salary ? x : y))
        : rows.reduce((x, y) => (x.salary < y.salary ? x : y));
    }
    case "get_weather":
      return weather(a.city);
    case "convert_currency":
      return currency(a.amount, a.from, a.to);
    case "get_time":
      return {
        timezone: a.timezone,
        time: new Intl.DateTimeFormat("en-IN", { timeZone: a.timezone, dateStyle: "full", timeStyle: "long" }).format(new Date()),
      };
    case "search_web":
      return webSearch(a.query);
    case "lookup_products": {
      const q = a.query.toLowerCase();
      return products.filter(
        (p) => (p.name.toLowerCase().includes(q) || p.category.toLowerCase().includes(q)) && (a.maxPrice == null || p.price <= a.maxPrice)
      );
    }
    case "calendar_check": {
      const rows = calendar.filter((x) => x.date.toLowerCase() === a.date.toLowerCase());
      return {
        date: a.date,
        availableSlots: rows.filter((x) => x.available && (a.preferredTime ? x.time === a.preferredTime : true)).map((x) => x.time),
        allSlots: rows,
      };
    }
    case "create_task": {
      // By the time we get here the user has already approved this call
      // (see requiresConfirmation + server/index.js).
      const task = { id: tasks.length + 1, title: a.title, priority: a.priority, createdAt: new Date().toISOString() };
      tasks.push(task);
      await saveTasks();
      return { created: true, task };
    }
    default:
      throw new Error("Unknown tool");
  }
}
