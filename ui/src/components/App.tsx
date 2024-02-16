import "./App.css";
import { HashRouter, Routes, Route } from "react-router-dom";
import Log from "./Log";
import Chat from "./Chat";
import Job from "./Job";
import Datasource from "./Datasource";
import Visuals from "./Visuals";

function App() {
  return (
    <Routes>
      <Route path="log" element={<Log />} />
      <Route path="job" element={<Job />} />
      <Route path="datasource" element={<Datasource />} />
      <Route path="/" element={<Chat />} />
      <Route path="/visuals" element={<Visuals />} />
    </Routes>
  );
}

export function WrappedApp() {
  return (
    <HashRouter>
      <App />
    </HashRouter>
  );
}