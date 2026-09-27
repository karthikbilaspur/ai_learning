import Console from "../components/Console";
import { tools } from "../data/tools";

const tool = tools.find((t) => t.path === "calendar")!;

export default function Calendar() {
  return <Console tool={tool} />;
}
