import Console from "../components/Console";
import { tools } from "../data/tools";

const tool = tools.find((t) => t.path === "calculator")!;

export default function Calculator() {
  return <Console tool={tool} />;
}
