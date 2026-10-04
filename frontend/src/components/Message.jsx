import Citation from "./Citation";

/* =========================================================
   MESSAGE COMPONENT
========================================================= */

export default function Message({
  message,
  onCopy,
  onFeedback,
  onRegenerate,
}) {
  const isUser =
    message.role === "user";

  /* =======================================================
     FORMAT RETRIEVAL SCORE
  ======================================================= */

  function formatScore(score) {
    if (
      score === null ||
      score === undefined ||
      Number.isNaN(Number(score))
    ) {
      return null;
    }

    const numericScore =
      Number(score);

    return numericScore <= 1
      ? `${(
          numericScore * 100
        ).toFixed(1)}%`
      : `${numericScore.toFixed(
          1
        )}%`;
  }

  /* =======================================================
     GROUNDING DATA
  ======================================================= */

  const grounding =
    message.grounding;

  const ruleResult =
    message.ruleResult;

  const retrievalScore =
    formatScore(
      message.retrievalScore
    );

  /* =======================================================
     RENDER
  ======================================================= */

  return (
    <div
      className={`message-row ${
        isUser
          ? "user-row"
          : "assistant-row"
      }`}
    >

      {/* =================================================
          AVATAR
      ================================================= */}

      <div
        className={`avatar ${
          isUser
            ? "user-avatar"
            : "assistant-avatar"
        }`}
      >
        {isUser
          ? "You"
          : "TG"}
      </div>

      {/* =================================================
          MESSAGE CONTENT
      ================================================= */}

      <div className="message-content">

        {/* Name */}

        <div className="message-name">
          {isUser
            ? "You"
            : "TruthGuard AI"}
        </div>

        {/* =================================================
            MESSAGE BUBBLE
        ================================================= */}

        <div
          className={`message-bubble ${
            isUser
              ? "user-bubble"
              : "assistant-bubble"
          }`}
        >
          {message.content
            .split("\n")
            .map(
              (line, index) => (
                <p key={index}>
                  {line || "\u00A0"}
                </p>
              )
            )}
        </div>

        {/* =================================================
            ASSISTANT INFORMATION
        ================================================= */}

        {!isUser && (
          <>

            {/* =============================================
                GROUNDING BADGE
            ============================================= */}

            {typeof message.grounded ===
              "boolean" && (
              <div
                className={`grounding-badge ${
                  message.grounded
                    ? "grounded"
                    : "not-grounded"
                }`}
              >
                {message.grounded
                  ? "✓ Grounded in college documents"
                  : "⚠ Not fully grounded"}
              </div>
            )}

            {/* =============================================
                GROUNDING DETAILS
            ============================================= */}

            {grounding && (
              <div className="grounding-details">

                <div>
                  <strong>
                    Grounding Coverage:
                  </strong>

                  {grounding.coverage !==
                    undefined &&
                  grounding.coverage !==
                    null
                    ? `${(
                        Number(
                          grounding.coverage
                        ) *
                        100
                      ).toFixed(1)}%`
                    : "N/A"}
                </div>

                {grounding.reason && (
                  <p>
                    <strong>
                      Reason:
                    </strong>

                    {grounding.reason}
                  </p>
                )}

                {Array.isArray(
                  grounding.found_terms
                ) &&
                  grounding
                    .found_terms
                    .length >
                    0 && (
                    <p>
                      <strong>
                        Supported:
                      </strong>{" "}
                      {grounding.found_terms.join(
                        ", "
                      )}
                    </p>
                  )}

                {Array.isArray(
                  grounding.missing_terms
                ) &&
                  grounding
                    .missing_terms
                    .length >
                    0 && (
                    <p>
                      <strong>
                        Missing:
                      </strong>{" "}
                      {grounding.missing_terms.join(
                        ", "
                      )}
                    </p>
                  )}

                {Array.isArray(
                  grounding.missing_entities
                ) &&
                  grounding
                    .missing_entities
                    .length >
                    0 && (
                    <p>
                      <strong>
                        Missing entities:
                      </strong>{" "}
                      {grounding.missing_entities.join(
                        ", "
                      )}
                    </p>
                  )}

              </div>
            )}

            {/* =============================================
                CITATIONS
            ============================================= */}

            {Array.isArray(
              message.citations
            ) &&
              message.citations.length >
                0 && (
                <Citation
                  citations={
                    message.citations
                  }
                />
              )}

            {/* =============================================
                RULE ENGINE
            ============================================= */}

            {ruleResult &&
              ruleResult.rule_found && (
                <div className="rule-card">

                  <div className="rule-header">

                    <span>
                      📋 Rule Evaluation
                    </span>

                    {typeof ruleResult.eligible ===
                      "boolean" && (
                      <span
                        className={
                          ruleResult.eligible
                            ? "eligible"
                            : "not-eligible"
                        }
                      >
                        {ruleResult.eligible
                          ? "Eligible"
                          : "Not Eligible"}
                      </span>
                    )}

                  </div>

                  <div className="rule-details">

                    {ruleResult.rule && (
                      <div>
                        Rule
                        <strong>
                          {
                            ruleResult.rule
                          }
                        </strong>
                      </div>
                    )}

                    {ruleResult.student_attendance !==
                      undefined && (
                      <div>
                        Student Attendance
                        <strong>
                          {
                            ruleResult.student_attendance
                          }
                          %
                        </strong>
                      </div>
                    )}

                    {ruleResult.required_attendance !==
                      undefined && (
                      <div>
                        Required Attendance
                        <strong>
                          {
                            ruleResult.required_attendance
                          }
                          %
                        </strong>
                      </div>
                    )}

                    {ruleResult.student_cgpa !==
                      undefined && (
                      <div>
                        Student CGPA
                        <strong>
                          {
                            ruleResult.student_cgpa
                          }
                        </strong>
                      </div>
                    )}

                    {ruleResult.required_cgpa !==
                      undefined && (
                      <div>
                        Required CGPA
                        <strong>
                          {
                            ruleResult.required_cgpa
                          }
                        </strong>
                      </div>
                    )}

                    {ruleResult.student_arrears !==
                      undefined && (
                      <div>
                        Student Arrears
                        <strong>
                          {
                            ruleResult.student_arrears
                          }
                        </strong>
                      </div>
                    )}

                    {ruleResult.maximum_arrears !==
                      undefined && (
                      <div>
                        Maximum Arrears
                        <strong>
                          {
                            ruleResult.maximum_arrears
                          }
                        </strong>
                      </div>
                    )}

                    {ruleResult.reason && (
                      <div className="rule-reason">
                        Reason
                        <strong>
                          {
                            ruleResult.reason
                          }
                        </strong>
                      </div>
                    )}

                  </div>

                </div>
              )}

            {/* =============================================
                RETRIEVAL SCORE
            ============================================= */}

            {retrievalScore && (
              <div className="retrieval-info">
                Retrieval confidence:{" "}
                {retrievalScore}
              </div>
            )}

            {/* =============================================
                MESSAGE ACTIONS
            ============================================= */}

            <div className="message-actions">

              {/* Copy */}

              <button
                onClick={() =>
                  onCopy(
                    message.content
                  )
                }
                title="Copy response"
                aria-label="Copy response"
              >
                📋
              </button>

              {/* Like */}

              <button
                className={
                  message.feedback ===
                  "up"
                    ? "feedback-active"
                    : ""
                }
                onClick={() =>
                  onFeedback(
                    message.id,
                    "up"
                  )
                }
                title="Good response"
                aria-label="Good response"
              >
                👍
              </button>

              {/* Dislike */}

              <button
                className={
                  message.feedback ===
                  "down"
                    ? "feedback-active"
                    : ""
                }
                onClick={() =>
                  onFeedback(
                    message.id,
                    "down"
                  )
                }
                title="Bad response"
                aria-label="Bad response"
              >
                👎
              </button>

              {/* Regenerate */}

              <button
                onClick={() =>
                  onRegenerate(
                    message.id
                  )
                }
                title="Regenerate response"
                aria-label="Regenerate response"
              >
                ↻
              </button>

            </div>

          </>
        )}

      </div>

    </div>
  );
}