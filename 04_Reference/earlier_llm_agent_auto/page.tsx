"use client";
import "@copilotkit/react-ui/styles.css";
import {
  CopilotChat,
  RenderMessage,
  CopilotChatSuggestion,
  RenderSuggestion,
  RenderSuggestionListProps,
} from "@copilotkit/react-ui";
import {
  useCopilotChat,
  useCopilotAction,
  CopilotKit,
} from "@copilotkit/react-core";
import type { Message as CopilotMessage } from "@copilotkit/shared";
import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  // TOOL CALLS for FRONTEND
  // rag_search
  useCopilotAction({
    name: "send_gantry_instructions",
    available: "frontend",
    render: ({ status, args }) => {
      return (
        <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 text-sm mt-2">
          <div className="animate-spin w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full"></div>
          {status !== "complete" && "Sending instructions..."}
          {status === "complete" && `Sent instructions`}
        </div>
      );
    },
  });

  // list_docs
  useCopilotAction({
    name: "get_container_positions",
    available: "frontend",
    render: ({ status, args }) => {
      return (
        <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 text-sm mt-2">
          <div className="animate-spin w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full"></div>
          {status !== "complete" && "Getting container positions..."}
          {status === "complete" && `Container positions: ${args}`}
        </div>
      );
    },
  });
  useCopilotAction({
    name: "get_weather",
    available: "frontend",
    render: ({ status, args }) => {
      return (
        <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 text-sm mt-2">
          <div className="animate-spin w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full"></div>
          {status !== "complete" && "Getting weather..."}
          {status === "complete" && `Weather: ${args}`}
        </div>
      );
    },
  });
  useCopilotAction({
    name: "get_current_day",
    available: "frontend",
    render: ({ status, args }) => {
      return (
        <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 text-sm mt-2">
          <div className="animate-spin w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full"></div>
          {status !== "complete" && "Getting current day..."}
          {status === "complete" && `Current day: ${args}`}
        </div>
      );
    },
  });

  return (
    <div className="min-h-screen flex">
      <main className="flex-1 p-6">
        <div className="max-w-4xl mx-auto">
          <CopilotChat
            labels={{
              title: "Your Assistant",
              initial: "Hi! 👋 How can I assist you today?",
            }}
          />
        </div>
      </main>
    </div>
  );
}
