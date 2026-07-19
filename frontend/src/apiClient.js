import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8010/api";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

let csrfToken = "";

function getCookie(name) {
  return document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${name}=`))
    ?.split("=")[1];
}

async function ensureCsrfToken() {
  if (!csrfToken) {
    const response = await apiClient.get("/auth/csrf/");
    csrfToken = response.data.csrf_token || getCookie("csrftoken") || "";
  }

  return csrfToken;
}

export function getErrorMessage(error, fallbackMessage) {
  const data = error.response?.data;

  if (!data) {
    return fallbackMessage;
  }

  if (typeof data.detail === "string") {
    return data.detail;
  }

  if (typeof data.non_field_errors?.[0] === "string") {
    return data.non_field_errors[0];
  }

  const firstError = Object.values(data).flat().find(Boolean);
  if (typeof firstError === "string") {
    return firstError;
  }

  return fallbackMessage;
}

export async function fetchCurrentUser() {
  const response = await apiClient.get("/auth/me/");
  return response.data.user;
}

export async function loginUser(credentials) {
  await ensureCsrfToken();

  const response = await apiClient.post("/auth/login/", credentials, {
    headers: { "X-CSRFToken": csrfToken },
  });

  csrfToken = response.data.csrf_token || csrfToken;
  return response.data.user;
}

export async function registerUser(userData) {
  await ensureCsrfToken();

  const response = await apiClient.post("/auth/register/", userData, {
    headers: { "X-CSRFToken": csrfToken },
  });

  csrfToken = response.data.csrf_token || csrfToken;
  return response.data.user;
}

export async function logoutUser() {
  await ensureCsrfToken();

  await apiClient.post(
    "/auth/logout/",
    {},
    {
      headers: { "X-CSRFToken": csrfToken },
    },
  );

  csrfToken = "";
}

export async function fetchContent() {
  const response = await apiClient.get("/content/");
  return response.data;
}

export async function submitContent(text) {
  await ensureCsrfToken();

  const response = await apiClient.post(
    "/content/",
    { text },
    {
      headers: { "X-CSRFToken": csrfToken },
    },
  );

  return response.data;
}

export async function fetchContentDetail(contentId) {
  const response = await apiClient.get(`/content/${contentId}/`);
  return response.data;
}
