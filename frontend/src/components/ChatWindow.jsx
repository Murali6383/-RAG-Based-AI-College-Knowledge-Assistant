import Message from "./Message";

/* =========================================================
   CHAT WINDOW
========================================================= */

export default function ChatWindow({
  messages = [],
  loading,
  onCopy,
  onFeedback,
  onRegenerate,
  onShare,
  onExport,
  onClear,
  onSuggestion,
}) {
  return (
    <div className="chat-window">

      {/* =================================================
          EMPTY / WELCOME SCREEN
      ================================================= */}

      {messages.length === 0 ? (
        <div className="welcome-screen">

          <div className="welcome-icon">
            TG
          </div>

          <h1>
            TruthGuard AI
          </h1>

          <p>
            Your grounded college
            knowledge assistant.
          </p>

          {/* Suggestions */}

          <div className="suggestion-grid">

            <button
              onClick={() =>
                onSuggestion(
                  "What are the hostel rules?"
                )
              }
            >
              <strong>
                🏠 Hostel Rules
              </strong>

              <span>
                Ask about hostel policies
              </span>
            </button>

            <button
              onClick={() =>
                onSuggestion(
                  "What is the minimum CGPA required for placement?"
                )
              }
            >
              <strong>
                🎓 Placement
              </strong>

              <span>
                Check placement eligibility
              </span>
            </button>

            <button
              onClick={() =>
                onSuggestion(
                  "What are the attendance requirements?"
                )
              }
            >
              <strong>
                📊 Attendance
              </strong>

              <span>
                Check attendance rules
              </span>
            </button>

            <button
              onClick={() =>
                onSuggestion(
                  "How do I apply for leave?"
                )
              }
            >
              <strong>
                📝 Leave Policy
              </strong>

              <span>
                Find leave procedures
              </span>
            </button>

          </div>

          <div className="welcome-note">
            Answers are generated only
            from your uploaded college
            documents.
          </div>

        </div>
      ) : (
        <>
          {/* =============================================
              CHAT TOOLBAR
          ============================================= */}

          <div className="chat-toolbar">

            <button
              onClick={onShare}
              disabled={loading}
              title="Share conversation"
              aria-label="Share conversation"
            >
              🔗 Share
            </button>

            <button
              onClick={onExport}
              disabled={loading}
              title="Export conversation"
              aria-label="Export conversation"
            >
              ⬇ Export
            </button>

            <button
              onClick={() => {
                if (loading) {
                  return;
                }

                const confirmed =
                  window.confirm(
                    "Clear this conversation?"
                  );

                if (confirmed) {
                  onClear();
                }
              }}
              disabled={loading}
              title="Clear conversation"
              aria-label="Clear conversation"
            >
              🧹 Clear
            </button>

          </div>

          {/* =============================================
              MESSAGES
          ============================================= */}

          <div className="messages-container">

            {messages.map(
              (message) => (
                <Message
                  key={message.id}
                  message={message}
                  onCopy={onCopy}
                  onFeedback={onFeedback}
                  onRegenerate={
                    onRegenerate
                  }
                />
              )
            )}

            {/* =========================================
                LOADING INDICATOR
            ========================================= */}

            {loading && (
              <div className="message-row assistant-row">

                <div className="avatar assistant-avatar">
                  TG
                </div>

                <div className="message-content">

                  <div className="message-name">
                    TruthGuard AI
                  </div>

                  <div className="typing-indicator">
                    <span />
                    <span />
                    <span />
                  </div>

                </div>

              </div>
            )}

          </div>
        </>
      )}

    </div>
  );
}