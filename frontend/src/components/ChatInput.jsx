import { useState } from "react";

export default function ChatInput({
  onSend,
  loading,
}) {
  const [value, setValue] =
    useState("");

  function submit() {
    if (!value.trim() || loading) {
      return;
    }

    onSend(value);
    setValue("");
  }

  function handleKeyDown(event) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      submit();
    }
  }

  return (
    <div className="input-area">

      <div className="input-wrapper">

        <textarea
          value={value}
          onChange={(event) =>
            setValue(event.target.value)
          }
          onKeyDown={handleKeyDown}
          placeholder={
            "Message TruthGuard AI..."
          }
          rows={1}
          disabled={loading}
        />

        <button
          className="send-button"
          onClick={submit}
          disabled={
            loading ||
            !value.trim()
          }
          aria-label="Send"
        >
          {loading ? "..." : "↑"}
        </button>

      </div>

      <div className="input-hint">
        TruthGuard AI can answer only
        from the provided documents.
        Press Enter to send · Shift + Enter
        for a new line.
      </div>

    </div>
  );
}