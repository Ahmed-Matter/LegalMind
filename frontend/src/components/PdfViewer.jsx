import { Document, Page } from "react-pdf";
import { useEffect } from "react";

export default function PdfViewer({
  fileUrl,
  page,
  highlightText,
  question,
  answer,
}) {
  useEffect(() => {
    let attempts = 0;

    const tryHighlight = () => {
      const textLayer = document.querySelector(".react-pdf__Page__textContent");

      if (!textLayer && attempts < 5) {
        attempts++;
        setTimeout(tryHighlight, 300);
        return;
      }

      highlight();
      scrollToHighlight();
    };

    setTimeout(tryHighlight, 500);
  }, [fileUrl, page, answer]);

  const normalize = (t) =>
    t.toLowerCase().replace(/[$,]/g, "").replace(/\s+/g, " ").trim();

  const highlight = () => {
    const textLayer = document.querySelector(".react-pdf__Page__textContent");
    if (!textLayer) return;

    const spans = Array.from(textLayer.querySelectorAll("span"));

    // clear previous highlights
    spans.forEach((span) => span.classList.remove("pdf-highlight"));

    const normalize = (t) =>
      t.toLowerCase().replace(/[$,]/g, "").replace(/\s+/g, " ").trim();

    const answerText = normalize(answer || "");
    if (!answerText) return;

    const numbers = answerText.match(/\d+/g) || [];
    const words = answerText.split(" ").filter((w) => w.length > 3);

    let bestMatch = null;
    let bestScore = 0;

    for (let i = 0; i < spans.length; i++) {
      let combined = "";
      let group = [];

      for (let j = i; j < Math.min(i + 8, spans.length); j++) {
        const text = normalize(spans[j].textContent);
        if (!text) continue;

        combined += " " + text;
        group.push(spans[j]);

        const combinedText = combined.trim();
        const combinedWords = combinedText.split(" ");

        let score = 0;

        numbers.forEach((n) => {
          if (combinedText.includes(n)) score += 10;
        });

        words.forEach((w) => {
          if (combinedWords.includes(w)) score += 2;
        });

        if (score > bestScore) {
          bestScore = score;
          bestMatch = group;
        }
      }
    }

    if (bestMatch && bestScore >= 10) {
      bestMatch.forEach((span) => span.classList.add("pdf-highlight"));
    }
  };

  const scrollToHighlight = () => {
    const first = document.querySelector(".pdf-highlight");
    if (first) {
      first.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }
  };

  return (
    <div className="p-4 overflow-auto h-full">
      <Document file={fileUrl}>
        <Page
          key={fileUrl + page} // ✅ CRITICAL
          pageNumber={page + 1}
          renderTextLayer
        />
      </Document>
    </div>
  );
}
