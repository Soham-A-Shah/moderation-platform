import React, { useState } from "react";
import { getErrorMessage, loginUser } from "../apiClient";

function LoginPage({ onLogin }) {
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    const formData = new FormData(event.currentTarget);

    try {
      const user = await loginUser({
        identifier: formData.get("identifier"),
        password: formData.get("password"),
      });

      onLogin(user);
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Unable to login."));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="card auth-card">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Email or username
          <input
            type="text"
            name="identifier"
            autoComplete="username"
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            name="password"
            autoComplete="current-password"
            required
          />
        </label>
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Logging in..." : "Login"}
        </button>
      </form>
      {error && <p className="form-message error-message">{error}</p>}
    </section>
  );
}

export default LoginPage;
