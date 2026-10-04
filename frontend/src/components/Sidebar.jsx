export default function Sidebar({
  chats,
  activeChatId,
  onNewChat,
  onSelectChat,
}) {
  return (
    <aside className="sidebar">

      <div className="sidebar-top">

        <div className="brand">

          <div className="brand-logo">
            TG
          </div>

          <div>
            <div className="brand-name">
              TruthGuard
            </div>

            <div className="brand-subtitle">
              AI Knowledge Assistant
            </div>
          </div>

        </div>

        <button
          className="new-chat-button"
          onClick={onNewChat}
        >
          <span>＋</span>
          New chat
        </button>

      </div>

      <div className="sidebar-section">

        <div className="sidebar-label">
          Recent chats
        </div>

        <div className="chat-history">

          {chats.length === 0 ? (
            <div className="empty-history">
              No conversations yet
            </div>
          ) : (
            chats.map((chat) => (
              <button
                key={chat.id}
                className={
                  chat.id === activeChatId
                    ? "history-item active"
                    : "history-item"
                }
                onClick={() =>
                  onSelectChat(chat.id)
                }
              >
                <span className="history-icon">
                  💬
                </span>

                <span className="history-title">
                  {chat.title}
                </span>
              </button>
            ))
          )}

        </div>

      </div>

      <div className="sidebar-bottom">

        <div className="knowledge-title">
          📚 Knowledge Base
        </div>

        <div className="document-item">
          <span>📘</span>
          College Regulations
        </div>

        <div className="document-item">
          <span>📊</span>
          Attendance Rules
        </div>

        <div className="document-item">
          <span>📝</span>
          Exam Regulations
        </div>

        <div className="document-item">
          <span>💼</span>
          Placement Guidelines
        </div>

        <div className="document-item">
          <span>🏠</span>
          Hostel Rules
        </div>

        <div className="document-item">
          <span>🗓️</span>
          Leave Policy
        </div>

        <div className="document-item">
          <span>🎓</span>
          Department Handbook
        </div>

        <div className="sidebar-status">
          <span className="status-dot"></span>
          Grounded RAG active
        </div>

      </div>

    </aside>
  );
}