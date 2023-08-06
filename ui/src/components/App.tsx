import "./App.css";
import { HashRouter, Routes, Route } from "react-router-dom";
import Log from "./Log";
import Chat from "./Chat";
import Job from "./Job";

function App() {
  return (
    <Routes>
      <Route path="log" element={<Log />} />
      <Route path="job" element={<Job />} />
      <Route path="/" element={<Chat />} />
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