// Central registry - import all 9 tools
import { calculatorTool } from './calculator';
import { webSearchTool } from './webSearch';
import { codeExecutorTool } from './codeExecutor';
import { fileReaderTool } from './fileReader';
import { weatherTool } from './weather';
import { calendarTool } from './calendar';
import { databaseQueryTool } from './databaseQuery';
import { imageGeneratorTool } from './imageGenerator';
import { memoryTool } from './memory';

export const allTools = {
  calculator: calculatorTool,
  web_search: webSearchTool,
  code_executor: codeExecutorTool,
  file_reader: fileReaderTool,
  weather: weatherTool,
  calendar: calendarTool,
  database_query: databaseQueryTool,
  image_generator: imageGeneratorTool,
  memory: memoryTool,
};

export type ToolName = keyof typeof allTools;
