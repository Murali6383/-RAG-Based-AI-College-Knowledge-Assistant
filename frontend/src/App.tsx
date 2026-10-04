import { useEffect, useState } from "react";

import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";

const API = "http://127.0.0.1:8000";

type Citation = {
  file: string;
  page: number | null;
  citation: string;
};

type Source = {
  file: string;
  page: number | null;
  score: number;
};

type RuleResult = {
  rule_found: boolean;
  rule?: string | null;
  result?: string;
  eligible?: boolean;
  student_attendance?: number;
  required_attendance?: number;
  student_cgpa?: number;
  required_cgpa?: number;
  student_arrears?: number;
  maximum_arrears?: number;
  reason?: string;
};

type Grounding = {
  supported: boolean;
  coverage: number;
  reason: string;
  found_terms?: string[];
  missing_terms?: string[];
  missing_entities?: string[];
};

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  grounded?: boolean;
  citations?: Citation[];
  sources?: Source[];
  retrievalScore?: number;
  ruleResult?: RuleResult | null;
  grounding?: Grounding | null;
};

type Chat = {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
};

const STORAGE_KEY = "truthguard_chats";

function createChat(): Chat {
  return {
    id: crypto.randomUUID(),
    title: "New Chat",
    messages: [],
    createdAt: Date.now(),
  };
}

export default function App() {
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChatId, setActiveChatId] = useState<string>("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);

      if (saved) {
        const parsed: Chat[] = JSON.parse(saved);

        if (parsed.length > 0) {
          setChats(parsed);
          setActiveChatId(parsed[0].id);
          return;
        }
      }
    } catch {
      console.log("Could not load saved chats");
    }

    const firstChat = createChat();

    setChats([firstChat]);
    setActiveChatId(firstChat.id);
  }, []);

  useEffect(() => {
    if (chats.length > 0) {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(chats)
      );
    }
  }, [chats]);

  const activeChat =
    chats.find((chat) => chat.id === activeChatId) ||
    null;

  function newChat() {
    const chat = createChat();

    setChats((previous) => [
      chat,
      ...previous,
    ]);

    setActiveChatId(chat.id);
  }

  function selectChat(id: string) {
    setActiveChatId(id);
  }

  function updateChat(
    chatId: string,
    updater: (chat: Chat) => Chat
  ) {
    setChats((previous) =>
      previous.map((chat) =>
        chat.id === chatId
          ? updater(chat)
          : chat
      )
    );
  }

  async function askQuestion(question: string) {
    if (!question.trim() || loading || !activeChat) {
      return;
    }

    const cleanQuestion = question.trim();

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: cleanQuestion,
    };

    updateChat(
      activeChat.id,
      (chat) => ({
        ...chat,
        title:
          chat.messages.length === 0
            ? cleanQuestion.length > 35
              ? cleanQuestion.substring(0, 35) + "..."
              : cleanQuestion
            : chat.title,
        messages: [
          ...chat.messages,
          userMessage,
        ],
      })
    );

    setLoading(true);

    try {
      const response = await fetch(
        `${API}/ask`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            question: cleanQuestion,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status}`
        );
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content:
          data.answer ||
          "I could not generate an answer.",
        grounded: data.grounded,
        citations: data.citations || [],
        sources: data.sources || [],
        retrievalScore:
          data.retrieval_score,
        ruleResult:
          data.rule_result || null,
        grounding:
          data.grounding || null,
      };

      updateChat(
        activeChat.id,
        (chat) => ({
          ...chat,
          messages: [
            ...chat.messages,
            assistantMessage,
          ],
        })
      );
    } catch (error) {
      console.error(error);

      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content:
          "I couldn't connect to TruthGuard AI. Please make sure the FastAPI backend is running on port 8000.",
        grounded: false,
        citations: [],
        sources: [],
      };

      updateChat(
        activeChat.id,
        (chat) => ({
          ...chat,
          messages: [
            ...chat.messages,
            errorMessage,
          ],
        })
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">

      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onNewChat={newChat}
        onSelectChat={selectChat}
      />

      <main className="main-area">

        <ChatWindow
          messages={
            activeChat?.messages || []
          }
          loading={loading}
        />

        <ChatInput
          onSend={askQuestion}
          loading={loading}
        />

      </main>

    </div>
  );
}