"use client";

import { useState } from "react";

export default function UploadPanel() {
  const [file, setFile] = useState<File | null>(null);

  const uploadFile = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    await fetch("http://localhost:8000/upload", {
      method: "POST",
      body: formData,
    });

    alert("File uploaded");
  };

  return (
    <div className="w-72 bg-gray-900 text-white p-4 flex flex-col gap-4">
      <h2 className="text-xl font-bold">Documents</h2>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
        className="text-sm"
      />

      <button
        onClick={uploadFile}
        className="bg-blue-500 hover:bg-blue-600 p-2 rounded"
      >
        Upload
      </button>
    </div>
  );
}
