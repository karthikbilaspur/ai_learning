import type { Tool } from "../types";

export const tools: Tool[] = [
  { path: "calculator", name: "Calculator", description: "Safe arithmetic tool.", example: "Calculate (783 * 42) / 6", kind: "info" },
  { path: "dataset", name: "Dataset Search", description: "Search employee data.", example: "Find engineering employees in Bengaluru", kind: "data" },
  { path: "analytics", name: "Data Analytics", description: "Calculate dataset statistics.", example: "What is the average engineering salary?", kind: "data" },
  { path: "weather", name: "Weather API", description: "Live Open-Meteo weather.", example: "What is the current weather in Bengaluru?", kind: "info" },
  { path: "currency", name: "Currency API", description: "Live exchange-rate conversion.", example: "Convert 50000 INR to USD", kind: "info" },
  { path: "time", name: "Time", description: "Current time by timezone.", example: "What time is it in Asia/Kolkata?", kind: "info" },
  { path: "web-search", name: "Web Search", description: "Web lookup tool.", example: "Search the web for TypeScript", kind: "info" },
  { path: "products", name: "Product Lookup", description: "Search the product catalog.", example: "Find laptops under 80000", kind: "data" },
  { path: "calendar", name: "Calendar", description: "Check demo availability.", example: "Check tomorrow's available meeting slots", kind: "action" },
  {
    path: "tasks",
    name: "Task Action",
    description: "Create a server-side task. Requires confirmation before it runs.",
    example: "Create a high priority task to review the agent demo",
    kind: "action",
  },
];
