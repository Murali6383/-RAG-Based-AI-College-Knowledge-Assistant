import { useEffect, useRef, useState } from "react";

export default function ChatInput({
  onSend,
  loading,
  onStop,
}) {
  const [value, setValue] =
    useState("");

  const textareaRef =
    useRef(null);

  /* =====================================================
     SUBMIT MESSAGE
  ===================================================== */

  function submit() {
    if (
      !value.trim() ||
      loading
    ) {
      return;
    }

    onSend(value.trim());

    setValue("");

    /* Reset textarea height */
    if (textareaRef.current) {
      textareaRef.current.style.height =
        "auto";
    }
  }

  /* =====================================================
     KEYBOARD HANDLER
  ===================================================== */

  function handleKeyDown(event) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      submit();
    }
  }

  /* =====================================================
     TEXTAREA CHANGE
  ===================================================== */

  function handleChange(event) {
    const newValue =
      event.target.value;

    setValue(newValue);

    const textarea =
      textareaRef.current;

    if (!textarea) {
      return;
    }

    textarea.style.height =
      "auto";

    textarea.style.height =
      `${Math.min(
        textarea.scrollHeight,
        160
      )}px`;
  }

  /* =====================================================
     AUTO FOCUS
  ===================================================== */

  useEffect(() => {
    if (!loading) {
      textareaRef.current?.focus();
    }
  }, [loading]);

  /* =====================================================
     RENDER
  ===================================================== */

  return (
    <div className="input-area">

      <div className="input-wrapper">

        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Message TruthGuard AI..."
          rows={1}
          disabled={loading}
          aria-label="Message TruthGuard AI"
        />

        {loading ? (
          <button
            className="stop-button"
            onClick={onStop}
            aria-label="Stop generating"
            title="Stop generating"
          >
            ■
          </button>
        ) : (
          <button
            className="send-button"
            onClick={submit}
            disabled={!value.trim()}
            aria-label="Send message"
            title="Send message"
          >
            ↑
          </button>
        )}

      </div>

      <div className="input-hint">
        TruthGuard AI answers from
        your provided college documents.
        <br />
        Enter to send · Shift + Enter
        for a new line.
      </div>

    </div>
  );
}