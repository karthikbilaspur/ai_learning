import fs from "node:fs/promises";

export const tools = [
  {
    type: "function",
    function: {
      name: "calculate",
      description: "Safely evaluate basic arithmetic using numbers and + - * / % parentheses.",
      parameters: {
        type: "object",
        properties: { expression: { type: "string" } },
        required: ["expression"],
        additionalProperties: false
      }
    }
  },
  {
    type: "function",
    function: {
      name: "search_dataset",
      description: "Search the demo employee dataset by name, department, city, or role.",
      parameters: {
        type: "object",
        properties: { query: { type: "string" } },
        required: ["query"],
        additionalProperties: false
      }
    }
  },
  {
    type: "function",
    function: {
      name: "analyze_dataset",
      description: "Calculate employee dataset statistics such as count, average salary, highest salary, or lowest salary.",
      parameters: {
        type: "object",
        properties: {
          metric: { type: "string", enum: ["count", "average_salary", "highest_salary", "lowest_salary"] },
          department: { type: "string" }
        },
        required: ["metric"],
        additionalProperties: false
      }
    }
  },
  {
    type: "function",
    function: {
      name: "get_weather",
      description: "Get current weather from Open-Meteo using a city name. No API key is required.",
      parameters: {
        type: "object",
        properties: { city: { type: "string" } },
        required: ["city"],
        additionalProperties: false
      }
    }
  },
  {
    type: "function",
    function: {
      name: "convert_currency",
      description: "Convert one currency amount to another using a live Frankfurter exchange-rate API.",
      parameters: {
        type: "object",
        properties: {
          amount: { type: "number" },
          from: { type: "string" },
          to: { type: "string" }
        },
        required: ["amount", "from", "to"],
        additionalProperties: false
      }
    }
  },
  {
    type: "function",
    function: {
      name: "get_time",
      description: "Get the current time for a city using its IANA time zone.",
      parameters: {
        type: "object",
        properties: {
          timezone: { type: "string", description: "Example: Asia/Kolkata" }
        },
        required: ["timezone"],
        additionalProperties: false
      }
    }
  },
  {
    type: "function",
    function: {
      name: "search_web",
      description: "Search the web through DuckDuckGo Instant Answer API for a topic.",
      parameters: {
        type: "object",
        properties: { query: { type: "string" } },
        required: ["query"],
        additionalProperties: false
      }
    }
  },
  {
    type: "function",
    function: {
      name: "lookup_products",
      description: "Search a local product catalog and optionally filter by maximum price.",
      parameters: {
        type: "object",
        properties: {
          query: { type: "string" },
          maxPrice: { type: "number" }
        },
        required: ["query"],
        additionalProperties: false
      }
    }
  },
  {
    type: "function",
    function: {
      name: "create_task",
      description: "Create a task in the demo in-memory task list.",
      parameters: {
        type: "object",
        properties: {
          title: { type: "string" },
          priority: { type: "string", enum: ["low", "medium", "high"] }
        },
        required: ["title"],
        additionalProperties: false
      }
    }
  }
];

const employees = JSON.parse(await fs.readFile(new URL("../data/employees.json", import.meta.url), "utf8"));

const products = [
  { id: "P1", name: "AeroBook 14", category: "laptop", price: 69999 },
  { id: "P2", name: "ProBook X", category: "laptop", price: 89999 },
  { id: "P3", name: "CodeMate 15", category: "laptop", price: 74999 },
  { id: "P4", name: "PixelPad", category: "tablet", price: 39999 },
  { id: "P5", name: "Vision Monitor 27", category: "monitor", price: 24999 }
];

const tasks = [];

function safeCalculate(expression) {
  if (!/^[0-9+\-*/%().\s]+$/.test(expression)) throw new Error("Unsupported expression");
  // Demo-only restricted arithmetic evaluator.
  return Function(`"use strict"; return (${expression})`)();
}

async function geocode(city) {
  const url = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1&language=en&format=json`;
  const r = await fetch(url);
  const data = await r.json();
  if (!data.results?.length) throw new Error(`City not found: ${city}`);
  return data.results[0];
}

async function getWeather(city) {
  const place = await geocode(city);
  const url = `https://api.open-meteo.com/v1/forecast?latitude=${place.latitude}&longitude=${place.longitude}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m`;
  const r = await fetch(url);
  const data = await r.json();
  return {
    city: place.name,
    country: place.country,
    temperatureC: data.current.temperature_2m,
    humidity: data.current.relative_humidity_2m,
    windKmh: data.current.wind_speed_10m,
    weatherCode: data.current.weather_code
  };
}

async function convertCurrency(amount, from, to) {
  const base = from.toUpperCase();
  const target = to.toUpperCase();
  const r = await fetch(`https://api.frankfurter.app/latest?amount=${amount}&from=${base}&to=${target}`);
  if (!r.ok) throw new Error("Currency API request failed");
  const data = await r.json();
  return { amount, from: base, to: target, converted: data.rates?.[target], date: data.date };
}

async function searchWeb(query) {
  const r = await fetch(`https://api.duckduckgo.com/?q=${encodeURIComponent(query)}&format=json&no_html=1&skip_disambig=0`);
  if (!r.ok) throw new Error("Web search failed");
  const data = await r.json();
  return {
    abstract: data.AbstractText || null,
    source: data.AbstractSource || null,
    url: data.AbstractURL || null,
    relatedTopics: (data.RelatedTopics || []).slice(0, 5).map(x => x.Text).filter(Boolean)
  };
}

export async function executeTool(name, args) {
  switch (name) {
    case "calculate":
      return { result: safeCalculate(args.expression) };

    case "search_dataset": {
      const q = args.query.toLowerCase();
      return employees.filter(e =>
        Object.values(e).some(v => String(v).toLowerCase().includes(q))
      );
    }

    case "analyze_dataset": {
      const rows = args.department
        ? employees.filter(e => e.department.toLowerCase() === args.department.toLowerCase())
        : employees;
      if (args.metric === "count") return { count: rows.length };
      if (!rows.length) return { error: "No matching employees" };
      const salaries = rows.map(e => e.salary);
      if (args.metric === "average_salary") return { averageSalary: salaries.reduce((a,b)=>a+b,0) / salaries.length };
      if (args.metric === "highest_salary") return rows.reduce((a,b)=>a.salary > b.salary ? a : b);
      if (args.metric === "lowest_salary") return rows.reduce((a,b)=>a.salary < b.salary ? a : b);
      return { error: "Unknown metric" };
    }

    case "get_weather":
      return getWeather(args.city);

    case "convert_currency":
      return convertCurrency(args.amount, args.from, args.to);

    case "get_time":
      return { timezone: args.timezone, time: new Intl.DateTimeFormat("en-IN", { timeZone: args.timezone, dateStyle: "full", timeStyle: "long" }).format(new Date()) };

    case "search_web":
      return searchWeb(args.query);

    case "lookup_products": {
      const q = args.query.toLowerCase();
      return products.filter(p =>
        (p.name.toLowerCase().includes(q) || p.category.toLowerCase().includes(q)) &&
        (args.maxPrice == null || p.price <= args.maxPrice)
      );
    }

    case "create_task": {
      const task = { id: tasks.length + 1, title: args.title, priority: args.priority || "medium", createdAt: new Date().toISOString() };
      tasks.push(task);
      return task;
    }

    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}