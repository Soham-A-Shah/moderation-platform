import React from "react";

function RecentContentList({ content, onRefresh }) {
  return (
    <section className="card">
      <div className="heading">
        <h2>Recent content</h2>
        <button type="button" onClick={onRefresh}>
          Refresh
        </button>
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
  );
}

export default RecentContentList;
