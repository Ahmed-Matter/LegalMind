"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import UploadPanel from "../components/UploadPanel";

type Message = {
  role: string;
  text: string;
};

export default function Home() {
  const router = useRouter();

  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      router.push("/login");
    }
  }, []);

  const sendMessage = async () => {
    if (!message) return;

    const userMessage: Message = {
      role: "user",
      text: message,
    };

    setMessages((prev) => [...prev, userMessage]);

    const response = await fetch(
      `http://localhost:8000/chat?question=${message}`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      },
    );

    const data = await response.json();

    const aiMessage: Message = {
      role: "assistant",
      text: data.answer,
    };

    setMessages((prev) => [...prev, aiMessage]);

    setMessage("");
  };
}
