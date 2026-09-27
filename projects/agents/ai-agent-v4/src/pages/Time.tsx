import Console from "../components/Console";
import { tools } from "../data/tools";

const tool = tools.find((t) => t.path === "time")!;

export default function Time() {
  return <Console tool={tool} />;
}
