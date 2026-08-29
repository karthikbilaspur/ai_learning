import { Route, Routes, useLocation } from "react-router-dom";
import Header from "./components/Header";
import ToolNav from "./components/ToolNav";
import { tools } from "./data/tools";
import Home from "./pages/Home";
import Calculator from "./pages/Calculator";
import DatasetSearch from "./pages/DatasetSearch";
import Analytics from "./pages/Analytics";
import Weather from "./pages/Weather";
import Currency from "./pages/Currency";
import Time from "./pages/Time";
import WebSearch from "./pages/WebSearch";
import Products from "./pages/Products";
import Calendar from "./pages/Calendar";
import Tasks from "./pages/Tasks";

// Maps each tool's `path` (from src/data/tools.ts) to its page component.
const pageByPath: Record<string, () => JSX.Element> = {
  calculator: Calculator,
  dataset: DatasetSearch,
  analytics: Analytics,
  weather: Weather,
  currency: Currency,
  time: Time,
  "web-search": WebSearch,
  products: Products,
  calendar: Calendar,
  tasks: Tasks,
};

function App() {
  const loc = useLocation();
  return (
    <div>
      <Header />
      <div className="layout">
        <ToolNav />
        <main>
          <div className="crumb">{loc.pathname}</div>
          <Routes>
            <Route path="/" element={<Home />} />
            {tools.map((t) => {
              const Page = pageByPath[t.path];
              return <Route key={t.path} path={"/" + t.path} element={<Page />} />;
            })}
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
