import React, { useState } from "react";
import { getErrorMessage, registerUser } from "../apiClient";

function RegisterPage({ onRegister }) {
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    const formData = new FormData(event.currentTarget);
    const password = formData.get("password");
    const confirmPassword = formData.get("confirmPassword");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);

    try {
      const user = await registerUser({
        first_name: formData.get("firstName"),
        last_name: formData.get("lastName"),
        username: formData.get("username"),
        email: formData.get("email"),
        password,
        confirm_password: confirmPassword,
      });

      onRegister(user);
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Unable to create account."));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="card auth-card">
      <h2>Register</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <label>
            First name
            <input
              type="text"
              name="firstName"
              autoComplete="given-name"
              required
            />
          </label>
          <label>
            Last name
            <input
              type="text"
              name="lastName"
              autoComplete="family-name"
              required
            />
          </label>
        </div>
        <label>
          Username
          <input type="text" name="username" autoComplete="username" required />
        </label>
        <label>
          Email
          <input type="email" name="email" autoComplete="email" required />
        </label>
        <label>
          Password
          <input
            type="password"
            name="password"
            autoComplete="new-password"
            required
          />
        </label>
        <label>
          Confirm password
          <input
            type="password"
            name="confirmPassword"
            autoComplete="new-password"
            required
          />
        </label>
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Creating account..." : "Create account"}
        </button>
      </form>
      {error && <p className="form-message error-message">{error}</p>}
    </section>
  );
}

export default RegisterPage;
