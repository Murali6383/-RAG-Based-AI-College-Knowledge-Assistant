import { useEffect, useState } from "react";

import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";

const API = "http://127.0.0.1:8000";
const STORAGE_KEY = "truthguard_chats";

/* =========================================================
   CREATE NEW CHAT
========================================================= */

function createChat() {
  return {
    id: crypto.randomUUID(),
    title: "New Chat",
    messages: [],
    createdAt: Date.now(),
    updatedAt: Date.now(),
    pinned: false,
  };
}

/* =========================================================
   MAIN APP
========================================================= */

export default function App() {
  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState("");

  const [loading, setLoading] = useState(false);

  const [controller, setController] = useState(null);

  /* =======================================================
     MOBILE SIDEBAR
  ======================================================= */

  const [sidebarOpen, setSidebarOpen] = useState(false);

  /* =======================================================
     LOAD CHATS FROM LOCAL STORAGE
  ======================================================= */

  useEffect(() => {
    try {
      const saved =
        localStorage.getItem(STORAGE_KEY);

      if (saved) {
        const parsed = JSON.parse(saved);

        if (
          Array.isArray(parsed) &&
          parsed.length > 0
        ) {
          setChats(parsed);
          setActiveChatId(parsed[0].id);
          return;
        }
      }
    } catch (error) {
      console.error(
        "Could not load saved chats:",
        error
      );
    }

    const firstChat = createChat();

    setChats([firstChat]);
    setActiveChatId(firstChat.id);
  }, []);

  /* =======================================================
     SAVE CHATS TO LOCAL STORAGE
  ======================================================= */

  useEffect(() => {
    if (chats.length > 0) {
      try {
        localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify(chats)
        );
      } catch (error) {
        console.error(
          "Could not save chats:",
          error
        );
      }
    }
  }, [chats]);

  /* =======================================================
     ACTIVE CHAT
  ======================================================= */

  const activeChat =
    chats.find(
      (chat) =>
        chat.id === activeChatId
    ) || null;

  /* =======================================================
     UPDATE CHAT
  ======================================================= */

  function updateChat(chatId, updater) {
    setChats((previous) =>
      previous.map((chat) =>
        chat.id === chatId
          ? updater(chat)
          : chat
      )
    );
  }

  /* =======================================================
     NEW CHAT
  ======================================================= */

  function newChat() {
    if (loading) {
      return;
    }

    const chat = createChat();

    setChats((previous) => [
      chat,
      ...previous,
    ]);

    setActiveChatId(chat.id);

    // Close mobile sidebar
    setSidebarOpen(false);
  }

  /* =======================================================
     SELECT CHAT
  ======================================================= */

  function selectChat(id) {
    if (loading) {
      return;
    }

    setActiveChatId(id);

    // Close mobile sidebar
    setSidebarOpen(false);
  }

  /* =======================================================
     RENAME CHAT
  ======================================================= */

  function renameChat(chatId, title) {
    const cleanTitle = title.trim();

    if (!cleanTitle) {
      return;
    }

    updateChat(
      chatId,
      (chat) => ({
        ...chat,
        title: cleanTitle,
        updatedAt: Date.now(),
      })
    );
  }

  /* =======================================================
     DELETE CHAT
  ======================================================= */

  function deleteChat(chatId) {
    if (loading) {
      return;
    }

    const confirmed =
      window.confirm(
        "Delete this conversation?"
      );

    if (!confirmed) {
      return;
    }

    const remaining =
      chats.filter(
        (chat) =>
          chat.id !== chatId
      );

    if (remaining.length === 0) {
      const freshChat =
        createChat();

      setChats([freshChat]);
      setActiveChatId(
        freshChat.id
      );

      return;
    }

    setChats(remaining);

    if (
      chatId === activeChatId
    ) {
      setActiveChatId(
        remaining[0].id
      );
    }
  }

  /* =======================================================
     PIN / UNPIN CHAT
  ======================================================= */

  function togglePin(chatId) {
    updateChat(
      chatId,
      (chat) => ({
        ...chat,
        pinned: !chat.pinned,
        updatedAt: Date.now(),
      })
    );
  }

  /* =======================================================
     CLEAR CURRENT CONVERSATION
  ======================================================= */

  function clearConversation(chatId) {
    updateChat(
      chatId,
      (chat) => ({
        ...chat,
        title: "New Chat",
        messages: [],
        updatedAt: Date.now(),
      })
    );
  }

  /* =======================================================
     UPDATE MESSAGE
  ======================================================= */

  function updateMessage(
    chatId,
    messageId,
    updater
  ) {
    updateChat(
      chatId,
      (chat) => ({
        ...chat,

        messages:
          chat.messages.map(
            (message) =>
              message.id ===
              messageId
                ? updater(message)
                : message
          ),

        updatedAt: Date.now(),
      })
    );
  }

  /* =======================================================
     ASK QUESTION
  ======================================================= */

  async function askQuestion(
    question,
    regenerate = false
  ) {
    if (
      !question ||
      !question.trim() ||
      loading ||
      !activeChat
    ) {
      return;
    }

    const cleanQuestion =
      question.trim();

    const chatId =
      activeChat.id;

    /* -----------------------------------------------------
       ADD USER MESSAGE
    ----------------------------------------------------- */

    if (!regenerate) {
      const userMessage = {
        id: crypto.randomUUID(),

        role: "user",

        content:
          cleanQuestion,
      };

      updateChat(
        chatId,
        (chat) => ({
          ...chat,

          title:
            chat.messages.length ===
            0
              ? cleanQuestion.length >
                40
                ? cleanQuestion.substring(
                    0,
                    40
                  ) + "..."
                : cleanQuestion
              : chat.title,

          messages: [
            ...chat.messages,
            userMessage,
          ],

          updatedAt: Date.now(),
        })
      );
    }

    /* -----------------------------------------------------
       START LOADING
    ----------------------------------------------------- */

    setLoading(true);

    const abortController =
      new AbortController();

    setController(
      abortController
    );

    try {
      /* ---------------------------------------------------
         BACKEND REQUEST
      --------------------------------------------------- */

      const response =
        await fetch(
          `${API}/ask`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify({
              question:
                cleanQuestion,
            }),

            signal:
              abortController.signal,
          }
        );

      /* ---------------------------------------------------
         HTTP ERROR
      --------------------------------------------------- */

      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status}`
        );
      }

      /* ---------------------------------------------------
         READ JSON RESPONSE
      --------------------------------------------------- */

      const data =
        await response.json();

      /* ---------------------------------------------------
         CREATE ASSISTANT MESSAGE
      --------------------------------------------------- */

      const assistantMessage = {
        id: crypto.randomUUID(),

        role: "assistant",

        content:
          data.answer ||
          "I could not generate an answer.",

        grounded:
          data.grounded,

        citations:
          Array.isArray(
            data.citations
          )
            ? data.citations
            : [],

        sources:
          Array.isArray(
            data.sources
          )
            ? data.sources
            : [],

        retrievalScore:
          data.retrieval_score,

        ruleResult:
          data.rule_result ||
          null,

        grounding:
          data.grounding ||
          null,

        feedback: null,
      };

      /* ---------------------------------------------------
         ADD ASSISTANT MESSAGE
      --------------------------------------------------- */

      updateChat(
        chatId,
        (chat) => ({
          ...chat,

          messages: [
            ...chat.messages,
            assistantMessage,
          ],

          updatedAt: Date.now(),
        })
      );
    } catch (error) {
      /* ---------------------------------------------------
         USER STOPPED REQUEST
      --------------------------------------------------- */

      if (
        error?.name ===
        "AbortError"
      ) {
        console.log(
          "Generation stopped by user."
        );

        return;
      }

      /* ---------------------------------------------------
         OTHER ERROR
      --------------------------------------------------- */

      console.error(
        "TruthGuard request failed:",
        error
      );

      const errorMessage = {
        id: crypto.randomUUID(),

        role: "assistant",

        content:
          "I couldn't connect to TruthGuard AI. Please make sure the FastAPI backend is running on port 8000.",

        grounded: false,

        citations: [],

        sources: [],

        retrievalScore: null,

        ruleResult: null,

        grounding: null,

        feedback: null,
      };

      updateChat(
        chatId,
        (chat) => ({
          ...chat,

          messages: [
            ...chat.messages,
            errorMessage,
          ],

          updatedAt: Date.now(),
        })
      );
    } finally {
      setLoading(false);
      setController(null);
    }
  }

  /* =======================================================
     STOP GENERATING
  ======================================================= */

  function stopGenerating() {
    if (!controller) {
      return;
    }

    controller.abort();

    setController(null);
    setLoading(false);
  }

  /* =======================================================
     REGENERATE RESPONSE
  ======================================================= */

  function regenerateMessage(
    messageId
  ) {
    if (
      loading ||
      !activeChat
    ) {
      return;
    }

    const index =
      activeChat.messages.findIndex(
        (message) =>
          message.id ===
          messageId
      );

    if (index === -1) {
      return;
    }

    /* -----------------------------------------------------
       FIND PREVIOUS USER QUESTION
    ----------------------------------------------------- */

    const lastUserMessage =
      [...activeChat.messages]
        .slice(0, index)
        .reverse()
        .find(
          (message) =>
            message.role ===
            "user"
        );

    if (!lastUserMessage) {
      return;
    }

    /* -----------------------------------------------------
       REMOVE OLD ASSISTANT RESPONSE
    ----------------------------------------------------- */

    updateChat(
      activeChat.id,
      (chat) => ({
        ...chat,

        messages:
          chat.messages.filter(
            (message) =>
              message.id !==
              messageId
          ),

        updatedAt: Date.now(),
      })
    );

    /* -----------------------------------------------------
       ASK SAME QUESTION AGAIN
    ----------------------------------------------------- */

    askQuestion(
      lastUserMessage.content,
      true
    );
  }

  /* =======================================================
     FEEDBACK
  ======================================================= */

  function giveFeedback(
    messageId,
    feedback
  ) {
    if (!activeChat) {
      return;
    }

    updateMessage(
      activeChat.id,
      messageId,
      (message) => ({
        ...message,

        feedback:
          message.feedback ===
          feedback
            ? null
            : feedback,
      })
    );
  }

  /* =======================================================
     COPY MESSAGE
  ======================================================= */

  async function copyMessage(
    content
  ) {
    try {
      await navigator.clipboard.writeText(
        content
      );
    } catch (error) {
      console.error(
        "Copy failed:",
        error
      );
    }
  }

  /* =======================================================
     SHARE CONVERSATION
  ======================================================= */

  async function shareConversation() {
    if (!activeChat) {
      return;
    }

    const text =
      activeChat.messages
        .map(
          (message) =>
            `${
              message.role ===
              "user"
                ? "You"
                : "TruthGuard AI"
            }:\n${
              message.content
            }`
        )
        .join("\n\n");

    if (
      navigator.share
    ) {
      try {
        await navigator.share({
          title:
            activeChat.title,

          text,
        });
      } catch (error) {
        console.log(
          "Share cancelled."
        );
      }

      return;
    }

    try {
      await navigator.clipboard.writeText(
        text
      );

      window.alert(
        "Conversation copied to clipboard."
      );
    } catch (error) {
      console.error(
        "Share failed:",
        error
      );
    }
  }

  /* =======================================================
     EXPORT CONVERSATION
  ======================================================= */

  function exportConversation() {
    if (!activeChat) {
      return;
    }

    const text =
      activeChat.messages
        .map(
          (message) =>
            `${
              message.role ===
              "user"
                ? "You"
                : "TruthGuard AI"
            }\n${
              message.content
            }`
        )
        .join(
          "\n\n--------------------\n\n"
        );

    const finalText =
      `TruthGuard AI\n` +
      `College Knowledge Assistant\n\n` +
      `${text}`;

    const blob =
      new Blob(
        [finalText],
        {
          type:
            "text/plain;charset=utf-8",
        }
      );

    const url =
      URL.createObjectURL(
        blob
      );

    const link =
      document.createElement(
        "a"
      );

    link.href = url;

    const safeTitle =
      activeChat.title
        .replace(
          /[^a-z0-9]/gi,
          "_"
        )
        .substring(
          0,
          40
        );

    link.download =
      `${
        safeTitle ||
        "truthguard-chat"
      }.txt`;

    document.body.appendChild(
      link
    );

    link.click();

    document.body.removeChild(
      link
    );

    URL.revokeObjectURL(
      url
    );
  }

  /* =======================================================
     RENDER
  ======================================================= */

  return (
    <div className="app-shell">

      {/* =================================================
          SIDEBAR
      ================================================= */}

      <Sidebar
        chats={chats}
        activeChatId={
          activeChatId
        }
        onNewChat={newChat}
        onSelectChat={
          selectChat
        }
        onRenameChat={
          renameChat
        }
        onDeleteChat={
          deleteChat
        }
        onTogglePin={
          togglePin
        }
        mobileOpen={
          sidebarOpen
        }
        onClose={() =>
          setSidebarOpen(false)
        }
      />

      {/* =================================================
          MAIN AREA
      ================================================= */}

      <main className="main-area">

        {/* =================================================
            MOBILE MENU BUTTON
        ================================================= */}

        <button
          className="mobile-menu-button"
          onClick={() =>
            setSidebarOpen(true)
          }
          aria-label="Open sidebar"
          title="Open sidebar"
        >
          ☰
        </button>

        {/* =================================================
            CHAT WINDOW
        ================================================= */}

        <ChatWindow
          messages={
            activeChat?.messages ||
            []
          }

          loading={loading}

          onCopy={
            copyMessage
          }

          onFeedback={
            giveFeedback
          }

          onRegenerate={
            regenerateMessage
          }

          onShare={
            shareConversation
          }

          onExport={
            exportConversation
          }

          onClear={() => {
            if (
              activeChat
            ) {
              clearConversation(
                activeChat.id
              );
            }
          }}

          onSuggestion={(
            question
          ) => {
            askQuestion(
              question
            );
          }}
        />

        {/* =================================================
            CHAT INPUT
        ================================================= */}

        <ChatInput
          onSend={(question) =>
            askQuestion(
              question
            )
          }
          loading={loading}
          onStop={
            stopGenerating
          }
        />

      </main>
    </div>
  );
}