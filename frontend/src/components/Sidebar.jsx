import { useMemo, useState } from "react";

/* =========================================================
   SIDEBAR
========================================================= */

export default function Sidebar({
  chats = [],
  activeChatId,
  onNewChat,
  onSelectChat,
  onRenameChat,
  onDeleteChat,
  onTogglePin,
  mobileOpen,
  onClose,
}) {
  const [search, setSearch] =
    useState("");

  const [editingChatId, setEditingChatId] =
    useState(null);

  const [editingTitle, setEditingTitle] =
    useState("");

  /* =======================================================
     FILTER + SORT CHATS
  ======================================================= */

  const filteredChats =
    useMemo(() => {
      const query =
        search
          .trim()
          .toLowerCase();

      const filtered =
        chats.filter((chat) => {
          if (!query) {
            return true;
          }

          const title =
            chat.title
              ?.toLowerCase() || "";

          const messages =
            chat.messages
              ?.map(
                (message) =>
                  message.content || ""
              )
              .join(" ")
              .toLowerCase() || "";

          return (
            title.includes(query) ||
            messages.includes(query)
          );
        });

      return [...filtered].sort(
        (a, b) => {
          if (
            Boolean(a.pinned) !==
            Boolean(b.pinned)
          ) {
            return a.pinned ? -1 : 1;
          }

          return (
            (b.updatedAt || 0) -
            (a.updatedAt || 0)
          );
        }
      );
    }, [chats, search]);

  /* =======================================================
     START RENAME
  ======================================================= */

  function startRename(
    event,
    chat
  ) {
    event.stopPropagation();

    setEditingChatId(chat.id);

    setEditingTitle(
      chat.title || ""
    );
  }

  /* =======================================================
     SAVE RENAME
  ======================================================= */

  function saveRename() {
    if (!editingChatId) {
      return;
    }

    const cleanTitle =
      editingTitle.trim();

    if (cleanTitle) {
      onRenameChat(
        editingChatId,
        cleanTitle
      );
    }

    setEditingChatId(null);
    setEditingTitle("");
  }

  /* =======================================================
     CANCEL RENAME
  ======================================================= */

  function cancelRename() {
    setEditingChatId(null);
    setEditingTitle("");
  }

  /* =======================================================
     RENAME KEYBOARD
  ======================================================= */

  function handleRenameKeyDown(
    event
  ) {
    if (event.key === "Enter") {
      event.preventDefault();
      saveRename();
    }

    if (event.key === "Escape") {
      event.preventDefault();
      cancelRename();
    }
  }

  /* =======================================================
     DELETE
  ======================================================= */

  function handleDelete(
    event,
    chatId
  ) {
    event.stopPropagation();

    onDeleteChat(chatId);
  }

  /* =======================================================
     PIN
  ======================================================= */

  function handlePin(
    event,
    chatId
  ) {
    event.stopPropagation();

    onTogglePin(chatId);
  }

  /* =======================================================
     SELECT CHAT
  ======================================================= */

  function handleSelectChat(
    chatId
  ) {
    if (
      editingChatId === chatId
    ) {
      return;
    }

    onSelectChat(chatId);

    // Close mobile sidebar
    if (onClose) {
      onClose();
    }
  }

  /* =======================================================
     NEW CHAT
  ======================================================= */

  function handleNewChat() {
    onNewChat();

    // Close mobile sidebar
    if (onClose) {
      onClose();
    }
  }

  /* =======================================================
     RENDER
  ======================================================= */

  return (
    <>
      {/* =================================================
          MOBILE BACKDROP
      ================================================= */}

      {mobileOpen && (
        <div
          className="sidebar-overlay"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* =================================================
          SIDEBAR
      ================================================= */}

      <aside
        className={`sidebar ${
          mobileOpen
            ? "mobile-open"
            : ""
        }`}
      >

        {/* =================================================
            MOBILE CLOSE BUTTON
        ================================================= */}

        <button
          className="mobile-close-button"
          onClick={onClose}
          aria-label="Close sidebar"
          title="Close sidebar"
        >
          ×
        </button>

        {/* =================================================
            SIDEBAR TOP
        ================================================= */}

        <div className="sidebar-top">

          {/* Brand */}

          <div className="brand">

            <div className="brand-logo">
              TG
            </div>

            <div>
              <div className="brand-name">
                TruthGuard AI
              </div>

              <div className="brand-subtitle">
                College Knowledge Assistant
              </div>
            </div>

          </div>

          {/* New Chat */}

          <button
            className="new-chat-button"
            onClick={handleNewChat}
            disabled={false}
          >
            <span>
              +
            </span>

            New Chat
          </button>

          {/* Search */}

          <div className="chat-search">

            <span>
              🔍
            </span>

            <input
              type="text"
              value={search}
              onChange={(event) =>
                setSearch(
                  event.target.value
                )
              }
              placeholder="Search conversations..."
              aria-label="Search conversations"
            />

            {search && (
              <button
                className="clear-search"
                onClick={() =>
                  setSearch("")
                }
                aria-label="Clear search"
                title="Clear search"
              >
                ×
              </button>
            )}

          </div>

        </div>

        {/* =================================================
            CHAT HISTORY
        ================================================= */}

        <div className="sidebar-section">

          <div className="sidebar-label">
            Conversations
          </div>

          <div className="chat-history">

            {filteredChats.length ===
            0 ? (
              <div className="empty-history">
                {search
                  ? "No conversations found."
                  : "No conversations yet."}
              </div>
            ) : (
              filteredChats.map(
                (chat) => (
                  <div
                    key={chat.id}
                    className={`history-item ${
                      chat.id ===
                      activeChatId
                        ? "active"
                        : ""
                    }`}
                    onClick={() =>
                      handleSelectChat(
                        chat.id
                      )
                    }
                  >

                    {/* =================================
                        CHAT MAIN
                    ================================= */}

                    {editingChatId ===
                    chat.id ? (
                      <input
                        className="rename-input"
                        value={
                          editingTitle
                        }
                        autoFocus
                        onChange={(event) =>
                          setEditingTitle(
                            event.target
                              .value
                          )
                        }
                        onKeyDown={
                          handleRenameKeyDown
                        }
                        onBlur={
                          saveRename
                        }
                        onClick={(event) =>
                          event.stopPropagation()
                        }
                      />
                    ) : (
                      <button
                        className="history-main"
                        onClick={() =>
                          handleSelectChat(
                            chat.id
                          )
                        }
                      >

                        <span className="history-icon">
                          {chat.pinned
                            ? "📌"
                            : "💬"}
                        </span>

                        <span className="history-title">
                          {chat.title ||
                            "New Chat"}
                        </span>

                      </button>
                    )}

                    {/* =================================
                        ACTIONS
                    ================================= */}

                    {editingChatId !==
                      chat.id && (
                      <div className="history-actions">

                        <button
                          onClick={(event) =>
                            handlePin(
                              event,
                              chat.id
                            )
                          }
                          title={
                            chat.pinned
                              ? "Unpin chat"
                              : "Pin chat"
                          }
                          aria-label={
                            chat.pinned
                              ? "Unpin chat"
                              : "Pin chat"
                          }
                        >
                          {chat.pinned
                            ? "📌"
                            : "📍"}
                        </button>

                        <button
                          onClick={(event) =>
                            startRename(
                              event,
                              chat
                            )
                          }
                          title="Rename chat"
                          aria-label="Rename chat"
                        >
                          ✎
                        </button>

                        <button
                          className="delete-chat"
                          onClick={(event) =>
                            handleDelete(
                              event,
                              chat.id
                            )
                          }
                          title="Delete chat"
                          aria-label="Delete chat"
                        >
                          🗑
                        </button>

                      </div>
                    )}

                  </div>
                )
              )
            )}

          </div>

        </div>

        {/* =================================================
            KNOWLEDGE BASE
        ================================================= */}

        <div className="sidebar-bottom">

          <div className="knowledge-title">
            Knowledge Base
          </div>

          <div className="document-item">
            <span>📄</span>
            <span>
              Attendance Rules
            </span>
          </div>

          <div className="document-item">
            <span>📄</span>
            <span>
              Exam Regulations
            </span>
          </div>

          <div className="document-item">
            <span>📄</span>
            <span>
              Placement Guidelines
            </span>
          </div>

          <div className="document-item">
            <span>📄</span>
            <span>
              Leave Policy
            </span>
          </div>

          {/* Status */}

          <div className="sidebar-status">

            <span className="status-dot" />

            TruthGuard AI Online

          </div>

        </div>

      </aside>
    </>
  );
}