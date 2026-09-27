import { Link } from "react-router-dom";

export default function Header() {
  return (
    <header>
      <Link to="/" className="brand">
        <span>V4</span> AI Agent Lab
      </Link>
      <small>React → Agent API → LLM → Tools → Result → LLM</small>
    </header>
  );
}
