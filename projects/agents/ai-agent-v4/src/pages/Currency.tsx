import Console from "../components/Console";
import { tools } from "../data/tools";

const tool = tools.find((t) => t.path === "currency")!;

export default function Currency() {
  return <Console tool={tool} />;
}
