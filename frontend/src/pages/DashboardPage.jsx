import React, { useEffect, useRef, useState } from "react";
import {
  fetchContent,
  fetchContentDetail,
  getErrorMessage,
  submitContent as submitContentRequest,
} from "../apiClient";
import ContentSubmissionForm from "../components/ContentSubmissionForm";
import RecentContentList from "../components/RecentContentList";

const DEFAULT_TEXT = "This is a normal travel post";

function DashboardPage() {
  const [text, setText] = useState(DEFAULT_TEXT);
  const [content, setContent] = useState([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const pollingTimer = useRef(null);

  async function refreshContent() {
    try {
      const nextContent = await fetchContent();
      setContent(nextContent);
      setError("");
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Unable to load content."));
    }
  }

  async function submitContent() {
    try {
      const response = await submitContentRequest(text);

      setMessage(`Submitted ${response.content_id}`);
      setError("");

      if (pollingTimer.current) {
        clearInterval(pollingTimer.current);
      }

      pollingTimer.current = setInterval(async () => {
        const result = await fetchContentDetail(response.content_id);

        await refreshContent();

        if (result.final_decision) {
          clearInterval(pollingTimer.current);
          pollingTimer.current = null;
        }
      }, 2000);
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Unable to submit content."));
    }
  }

  useEffect(() => {
    refreshContent();

    return () => {
      if (pollingTimer.current) {
        clearInterval(pollingTimer.current);
      }
    };
  }, []);

  return (
    <>
      <ContentSubmissionForm
        error={error}
        message={message}
        text={text}
        onSubmit={submitContent}
        onTextChange={setText}
      />
      <RecentContentList content={content} onRefresh={refreshContent} />
    </>
  );
}

export default DashboardPage;
