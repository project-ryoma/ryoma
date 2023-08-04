import "./App.css";
import { HashRouter, Routes, Route } from "react-router-dom";
import Log from "./Log";
import Chat from "./Chat";

function App() {
  return (
    <Routes>
      <Route path="log" element={<Log />} />
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