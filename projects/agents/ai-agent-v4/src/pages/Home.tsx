import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="home">
      <span className="pill action">V4 UPGRADE</span>
      <h1>LLM-driven multi-step AI agent.</h1>
      <p>
        V4 splits the app into components and a dedicated page per tool, adds a human-in-the-loop confirmation
        step for actions that change state, persists tasks to disk, times out slow third-party API calls, and
        locks down CORS and request rate limits on the server.
      </p>
      <div className="stats">
        <div>
          <b>10</b>
          <span>tools</span>
        </div>
        <div>
          <b>8</b>
          <span>agent rounds</span>
        </div>
        <div>
          <b>1</b>
          <span>confirm-before-act tool</span>
        </div>
      </div>
      <p className="example">
        Try: "Check Bengaluru weather, find the average engineering salary, and convert that salary from INR to
        USD."
      </p>
      <Link to="/weather" className="start">
        Open workspace →
      </Link>
    </div>
  );
}
