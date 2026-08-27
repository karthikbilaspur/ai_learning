import Console from "../components/Console";
import { tools } from "../data/tools";

const tool = tools.find((t) => t.path === "tasks")!;

export default function Tasks() {
  return (
    <div>
      <div className="notice">
        New in v4: this action changes server state, so the agent will pause and ask you to approve or reject it
        before it runs.
      </div>
      <Console tool={tool} />
    </div>
  );
}
