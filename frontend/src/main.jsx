import "./pdfWorker";
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";
import { pdfjs } from "react-pdf";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

//pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;
