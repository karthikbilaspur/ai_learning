import Console from "../components/Console";
import { tools } from "../data/tools";

const tool = tools.find((t) => t.path === "products")!;

export default function Products() {
  return <Console tool={tool} />;
}
