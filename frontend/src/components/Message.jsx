import Citation from "./Citation";

export default function Message({
  message,
}) {
  const isUser =
    message.role === "user";

  return (
    <div
      className={
        isUser
          ? "message-row user-row"
          : "message-row assistant-row"
      }
    >

      <div
        className={
          isUser
            ? "avatar user-avatar"
            : "avatar assistant-avatar"
        }
      >
        {isUser ? "You" : "TG"}
      </div>

      <div className="message-content">

        <div className="message-name">
          {isUser
            ? "You"
            : "TruthGuard AI"}
        </div>

        <div
          className={
            isUser
              ? "message-bubble user-bubble"
              : "message-bubble assistant-bubble"
          }
        >
          {message.content
            .split("\n")
            .map((line, index) => (
              <p key={index}>
                {line || "\u00A0"}
              </p>
            ))}
        </div>

        {!isUser &&
          message.grounded !==
            undefined && (
            <div
              className={
                message.grounded
                  ? "grounding-badge grounded"
                  : "grounding-badge not-grounded"
              }
            >
              {message.grounded
                ? "✓ Grounded in documents"
                : "⚠ Not grounded"}
            </div>
          )}

        {!isUser &&
          message.ruleResult
            ?.rule_found && (
            <RuleResult
              result={message.ruleResult}
            />
          )}

        {!isUser &&
          message.citations &&
          message.citations.length >
            0 && (
            <Citation
              citations={
                message.citations
              }
            />
          )}

        {!isUser &&
          message.retrievalScore !==
            undefined && (
            <div className="retrieval-info">
              Retrieval confidence:{" "}
              {(
                message.retrievalScore *
                100
              ).toFixed(1)}
              %
            </div>
          )}

      </div>

    </div>
  );
}

function RuleResult({ result }) {
  const isEligible =
    result.eligible === true;

  return (
    <div className="rule-card">

      <div className="rule-header">
        <span>⚙️ Rule Engine</span>

        <span
          className={
            isEligible
              ? "eligible"
              : "not-eligible"
          }
        >
          {result.result}
        </span>
      </div>

      {result.rule ===
        "minimum_attendance" && (
        <div className="rule-details">

          <div>
            Your attendance
            <strong>
              {result.student_attendance}%
            </strong>
          </div>

          <div>
            Required attendance
            <strong>
              {result.required_attendance}%
            </strong>
          </div>

        </div>
      )}

      {result.rule ===
        "minimum_cgpa" && (
        <div className="rule-details">

          <div>
            Your CGPA
            <strong>
              {result.student_cgpa}
            </strong>
          </div>

          <div>
            Required CGPA
            <strong>
              {result.required_cgpa}
            </strong>
          </div>

        </div>
      )}

      {result.rule ===
        "maximum_arrears" && (
        <div className="rule-details">

          <div>
            Your arrears
            <strong>
              {result.student_arrears}
            </strong>
          </div>

          <div>
            Maximum allowed
            <strong>
              {result.maximum_arrears}
            </strong>
          </div>

        </div>
      )}

    </div>
  );
}