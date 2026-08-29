import Console from "../components/Console";
import { tools } from "../data/tools";

const tool = tools.find((t) => t.path === "dataset")!;

export default function DatasetSearch() {
  return <Console tool={tool} />;
}
