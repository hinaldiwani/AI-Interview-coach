/* Centralized API Service for AI Interview Coach */
const API_BASE_URL = "";

class ApiService {
  static getAuthToken() {
    return localStorage.getItem("token") || null;
  }

  static async request(endpoint, options = {}) {
    const token = this.getAuthToken();
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {})
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const config = {
      ...options,
      headers
    };

    try {
      const response = await fetch(API_BASE_URL + endpoint, config);
      const data = await response.json();

      if (!response.ok) {
        if (response.status === 401 && !endpoint.includes("/login")) {
          // Token expired, clear auth & redirect
          localStorage.removeItem("token");
          localStorage.removeItem("user");
          window.location.href = "login.html";
        }
        throw new Error(data.detail || data.message || "API request failed.");
      }
      return data;
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // Auth Endpoints
  static async register(name, email, password) {
    return this.request("/api/register", {
      method: "POST",
      body: JSON.stringify({ name, email, password })
    });
  }

  static async login(email, password) {
    return this.request("/api/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
  }

  static async logout() {
    try {
      await this.request("/api/logout", { method: "POST" });
    } catch (e) {}
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "login.html";
  }

  static async getProfile() {
    return this.request("/api/user/profile");
  }

  // Interview Endpoints
  static async createInterview(role, experience, interview_type, difficulty, total_questions) {
    return this.request("/api/interviews", {
      method: "POST",
      body: JSON.stringify({ role, experience, interview_type, difficulty, total_questions })
    });
  }

  static async submitAnswer(interviewId, questionId, userAnswer) {
    return this.request(`/api/interviews/${interviewId}/answer`, {
      method: "POST",
      body: JSON.stringify({ question_id: questionId, user_answer: userAnswer })
    });
  }

  static async completeInterview(interviewId) {
    return this.request(`/api/interviews/${interviewId}/complete`, {
      method: "POST"
    });
  }

  static async getInterviewResults(interviewId) {
    return this.request(`/api/interviews/${interviewId}/results`);
  }

  // Dashboard & History Endpoints
  static async getDashboard() {
    return this.request("/api/dashboard");
  }

  static async getHistory() {
    return this.request("/api/history");
  }
}
