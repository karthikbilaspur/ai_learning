import Console from "../components/Console";
import { tools } from "../data/tools";

const tool = tools.find((t) => t.path === "web-search")!;

export default function WebSearch() {
  return <Console tool={tool} />;
}
