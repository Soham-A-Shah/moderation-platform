import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import axios from "axios";
import "./styles.css";

const API_URL = "http://localhost:8010/api";

function App() {
  const [text, setText] = useState("This is a normal travel post");
  const [content, setContent] = useState([]);
  const [message, setMessage] = useState("");

  async function refresh() {
    const response = await axios.get(`${API_URL}/content/`);
    setContent(response.data);
  }

  async function submit() {
    const response = await axios.post(`${API_URL}/content/`, {
      user_id: "demo-user",
      text,
    });

    setMessage(`Submitted ${response.data.content_id}`);

    const timer = setInterval(async () => {
      const result = await axios.get(
        `${API_URL}/content/${response.data.content_id}/`,
      );

      await refresh();

      if (result.data.final_decision) {
        clearInterval(timer);
      }
    }, 2000);
  }

  useEffect(() => {
    refresh();
  }, []);

  return (
    <main>
      <header>
        <h1>Content Moderation Platform</h1>
        <p>Django, Kafka, PostgreSQL, Docker, and Kubernetes</p>
      </header>

      <section className="card">
        <h2>Submit content</h2>
        <textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
        />
        <button onClick={submit}>Submit to pipeline</button>
        {message && <p>{message}</p>}
        <small>Try: buy now free money spam scam</small>
      </section>

      <section className="card">
        <div className="heading">
          <h2>Recent content</h2>
          <button onClick={refresh}>Refresh</button>
        </div>

        <div className="items">
          {content.map((item) => (
            <article key={item.id}>
              <div className="heading">
                <strong>{item.user_id}</strong>
                <span className={`badge ${item.final_decision || item.status}`}>
                  {item.final_decision || item.status}
                </span>
              </div>
              <p>{item.text}</p>
              <small>
                {item.reason || "Waiting for asynchronous moderation..."}
              </small>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
