import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { fetchCurrentUser, getErrorMessage, logoutUser } from "./apiClient";
import AppHeader from "./components/AppHeader";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import "./styles.css";

const PAGES = {
  dashboard: "dashboard",
  login: "login",
  register: "register",
};

function App() {
  const [activePage, setActivePage] = useState(PAGES.login);
  const [authError, setAuthError] = useState("");
  const [isLoadingUser, setIsLoadingUser] = useState(true);
  const [user, setUser] = useState(null);

  useEffect(() => {
    async function loadCurrentUser() {
      try {
        const currentUser = await fetchCurrentUser();
        setUser(currentUser);
        setActivePage(PAGES.dashboard);
      } catch {
        setUser(null);
        setActivePage(PAGES.login);
      } finally {
        setIsLoadingUser(false);
      }
    }

    loadCurrentUser();
  }, []);

  function handleAuthenticated(nextUser) {
    setAuthError("");
    setUser(nextUser);
    setActivePage(PAGES.dashboard);
  }

  async function handleLogout() {
    try {
      await logoutUser();
      setUser(null);
      setActivePage(PAGES.login);
    } catch (error) {
      setAuthError(getErrorMessage(error, "Unable to logout."));
    }
  }

  const pages = {
    [PAGES.dashboard]: user ? (
      <DashboardPage />
    ) : (
      <LoginPage onLogin={handleAuthenticated} />
    ),
    [PAGES.login]: <LoginPage onLogin={handleAuthenticated} />,
    [PAGES.register]: <RegisterPage onRegister={handleAuthenticated} />,
  };

  if (isLoadingUser) {
    return (
      <main>
        <section className="card auth-card">
          <h2>Loading</h2>
          <p>Checking your session...</p>
        </section>
      </main>
    );
  }

  return (
    <main>
      <AppHeader
        activePage={activePage}
        onLogout={handleLogout}
        onPageChange={setActivePage}
        user={user}
      />
      {authError && <p className="form-message error-message">{authError}</p>}
      {pages[activePage]}
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
