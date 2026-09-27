import { tool } from 'ai';
import { z } from 'zod';

export const weatherTool = tool({
  description: 'Get current weather for any city. Use when user asks about weather, forecast, temperature.',
  parameters: z.object({
    city: z.string().describe('City name, e.g. "Bangalore"'),
    unit: z.enum(['celsius', 'fahrenheit']).default('celsius').optional(),
  }),
  execute: async ({ city, unit = 'celsius' }) => {
    const key = process.env.OPENWEATHER_API_KEY;
    if (!key) return { city, warning: 'OPENWEATHER_API_KEY not set - mock data', temp: '28C', condition: 'Partly Cloudy (mock)' };
    const res = await fetch(`https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(city)}&appid=${key}&units=${unit === 'celsius' ? 'metric' : 'imperial'}`);
    const data = await res.json();
    if (data.cod !== 200) return { city, error: data.message };
    return { city, temp: data.main.temp, feels_like: data.main.feels_like, condition: data.weather[0].description, humidity: data.main.humidity, unit };
  },
});
