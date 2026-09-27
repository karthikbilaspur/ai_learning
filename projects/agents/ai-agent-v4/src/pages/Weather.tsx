import Console from "../components/Console";
import { tools } from "../data/tools";

const tool = tools.find((t) => t.path === "weather")!;

export default function Weather() {
  return <Console tool={tool} />;
}
