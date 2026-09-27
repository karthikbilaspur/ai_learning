import Console from "../components/Console";
import { tools } from "../data/tools";

const tool = tools.find((t) => t.path === "analytics")!;

export default function Analytics() {
  return <Console tool={tool} />;
}
