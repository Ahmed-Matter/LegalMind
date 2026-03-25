import { Document, Page } from "react-pdf";
import { useEffect } from "react";

export default function PdfViewer({ fileUrl, page, highlightText }) {
  useEffect(() => {
    setTimeout(() => highlight(), 500);
  }, [page, highlightText]);

  const highlight = () => {
    if (!highlightText) return;

    const textLayer = document.querySelector(".react-pdf__Page__textContent");
    if (!textLayer) return;

    const spans = textLayer.querySelectorAll("span");

    spans.forEach((span) => {
      const text = span.textContent.toLowerCase();

      if (highlightText.toLowerCase().includes(text) && text.length > 5) {
        span.style.backgroundColor = "yellow";
      }
    });
  };

  return (
    <div className="p-4 overflow-auto h-full">
      <Document file={fileUrl}>
        <Page pageNumber={page + 1} renderTextLayer />
      </Document>
    </div>
  );
}
