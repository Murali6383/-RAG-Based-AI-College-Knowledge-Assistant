import Message from "./Message";

export default function ChatWindow({
  messages,
  loading,
}) {
  return (
    <div className="chat-window">

      {messages.length === 0 ? (
        <div className="welcome-screen">

          <div className="welcome-icon">
            TG
          </div>

          <h1>
            TruthGuard AI
          </h1>

          <p>
            Your grounded college knowledge
            assistant.
          </p>

          <div className="suggestion-grid">

            <button>
              What are the hostel rules?
            </button>

            <button>
              What is the minimum CGPA
              required for placement?
            </button>

            <button>
              What are the attendance
              requirements?
            </button>

            <button>
              How do I apply for leave?
            </button>

          </div>

          <div className="welcome-note">
            Answers are generated only from
            your uploaded college documents.
          </div>

        </div>
      ) : (
        <div className="messages-container">

          {messages.map((message) => (
            <Message
              key={message.id}
              message={message}
            />
          ))}

          {loading && (
            <div className="message-row assistant-row">

              <div className="avatar assistant-avatar">
                TG
              </div>

              <div className="message-content">

                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>

              </div>

            </div>
          )}

        </div>
      )}

    </div>
  );
}