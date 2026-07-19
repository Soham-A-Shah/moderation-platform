import React from "react";

const NAV_ITEMS = [
  { id: "dashboard", label: "Dashboard" },
  { id: "login", label: "Login" },
  { id: "register", label: "Register" },
];

function AppHeader({ activePage, onLogout, onPageChange, user }) {
  const visibleNavItems = user
    ? NAV_ITEMS.filter((item) => item.id === "dashboard")
    : NAV_ITEMS.filter((item) => item.id !== "dashboard");

  return (
    <header>
      <nav aria-label="Primary navigation">
        {visibleNavItems.map((item) => (
          <button
            key={item.id}
            className={activePage === item.id ? "nav-active" : ""}
            type="button"
            onClick={() => onPageChange(item.id)}
          >
            {item.label}
          </button>
        ))}
        {user && (
          <button type="button" onClick={onLogout}>
            Logout
          </button>
        )}
      </nav>
      <h1>Content Moderation Platform</h1>
      <p>
        {user
          ? `Signed in as ${user.username}`
          : "Django, Kafka, PostgreSQL, Docker, and Kubernetes"}
      </p>
    </header>
  );
}

export default AppHeader;
