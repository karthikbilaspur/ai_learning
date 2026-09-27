import { NavLink } from "react-router-dom";
import { tools } from "../data/tools";

export default function ToolNav() {
  return (
    <aside>
      <label>TOOLS</label>
      {tools.map((t) => (
        <NavLink key={t.path} to={"/" + t.path} className={({ isActive }) => (isActive ? "nav active" : "nav")}>
          {t.name}
          <small>{t.kind}</small>
        </NavLink>
      ))}
    </aside>
  );
}
