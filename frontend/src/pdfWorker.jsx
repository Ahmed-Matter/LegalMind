import { pdfjs } from "react-pdf";
import worker from "pdfjs-dist/build/pdf.worker.min.mjs?url";

pdfjs.GlobalWorkerOptions.workerSrc = worker;
