export default function Citation({
  citations = [],
}) {
  if (!citations.length) {
    return null;
  }

  return (
    <div className="citations">

      <div className="citation-title">
        📚 Sources
      </div>

      <div className="citation-list">

        {citations.map(
          (citation, index) => (
            <div
              className="citation-item"
              key={`${citation.file}-${citation.page}-${index}`}
            >

              <span className="pdf-icon">
                📄
              </span>

              <span className="citation-file">
                {citation.file}
              </span>

              {citation.page !== null &&
                citation.page !== undefined && (
                  <span className="page-number">
                    Page {citation.page}
                  </span>
                )}

            </div>
          )
        )}

      </div>

    </div>
  );
}