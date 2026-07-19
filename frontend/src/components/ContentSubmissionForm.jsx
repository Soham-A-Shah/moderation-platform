import React from "react";

function ContentSubmissionForm({ error, message, text, onSubmit, onTextChange }) {
  return (
    <section className="card">
      <h2>Submit content</h2>
      <textarea
        value={text}
        onChange={(event) => onTextChange(event.target.value)}
      />
      <button type="button" onClick={onSubmit}>
        Submit to pipeline
      </button>
      {message && <p>{message}</p>}
      {error && <p className="form-message error-message">{error}</p>}
      <small>Try: buy now free money spam scam</small>
    </section>
  );
}

export default ContentSubmissionForm;
