import { tool } from 'ai';
import { z } from 'zod';

// Mock - replace with Google Calendar API later
const MOCK_EVENTS = [
  { id: '1', title: 'Team Standup', start: '2026-08-29T09:30:00+05:30', end: '2026-08-29T10:00:00+05:30' },
  { id: '2', title: 'Client Call', start: '2026-08-29T14:00:00+05:30', end: '2026-08-29T15:00:00+05:30' },
];

export const calendarTool = tool({
  description: 'Check calendar availability, list events, find free slots. Use for scheduling tasks.',
  parameters: z.object({
    action: z.enum(['list', 'check_availability', 'find_free_slot']).default('list'),
    date: z.string().describe('Date in YYYY-MM-DD').optional(),
    timeRange: z.string().describe('e.g. "09:00-17:00"').optional(),
  }),
  execute: async ({ action, date, timeRange }) => {
    if (action === 'list') {
      return { events: MOCK_EVENTS, date: date || 'today' };
    }
    if (action === 'check_availability') {
      return { date, timeRange, available: true, conflicts: [] };
    }
    return { date, freeSlots: ['09:00-09:30', '10:00-14:00', '15:30-18:00'] };
  },
});
