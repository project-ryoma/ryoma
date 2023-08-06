import React from 'react';
import "./index.css";
import ReactDOM from 'react-dom/client';
import { WrappedApp } from "./components/App";
import reportWebVitals from './reportWebVitals';
import axios from "axios";

axios.defaults.baseURL = process.env.NODE_ENV === 'production' ? "https://infiniteai.azurewebsites.net/" : "locahost:3001";

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <WrappedApp />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
