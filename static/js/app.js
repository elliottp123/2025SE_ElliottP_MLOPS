// core app functionality classes and utilities

class PrivacyManager {
  constructor() {
    this.bindPrivacyEvents();
  }

  bindPrivacyEvents() {
    const downloadBtn = document.getElementById("downloadData");
    const deleteBtn = document.getElementById("deleteAccount");

    if (downloadBtn) {
      downloadBtn.addEventListener("click", () => this.handleDownload());
    }
    if (deleteBtn) {
      deleteBtn.addEventListener("click", () => this.handleDelete());
    }
  }

  async handleDownload() {
    try {
      const response = await fetch("/api/user/data");
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "my_devlog_data.json";
      a.click();
    } catch (error) {
      showNotification("failed to download data", "error");
    }
  }

  async handleDelete() {
    if (confirm("are you sure? this action cannot be undone")) {
      try {
        const response = await fetch("/api/user/data", {
          method: "DELETE",
          headers: {
            "X-CSRF-TOKEN": document.querySelector('meta[name="csrf-token"]')
              .content,
          },
        });
        if (response.ok) {
          window.location.href = "/login";
        }
      } catch (error) {
        showNotification("failed to delete account", "error");
      }
    }
  }
}

class ProfileManager {
  constructor() {
    this.bindApiKeyEvents();
    this.loadProfileData();
    this.bind2FAEvents();
  }

  initializeErrorHandling() {
    this.errorContainer = document.createElement("div");
    this.errorContainer.className = "alert alert-danger";
    document.querySelector(".container").prepend(this.errorContainer);
  }

  showNotification(message, type = "danger") {
    const notification = document.createElement("div");
    notification.className = `alert alert-${type} fade show`;
    notification.textContent = message;
    document.querySelector(".container").prepend(notification);
    setTimeout(() => notification.remove(), 3000);
  }

  logError(error, context) {
    console.error(`Error in ${context}:`, error);
    this.showNotification(`${context}: ${error.message}`);
  }

  bindApiKeyEvents() {
    document
      .getElementById("generateApiKey")
      ?.addEventListener("click", () => this.handleGenerateKey());
    document
      .getElementById("regenerateApiKey")
      ?.addEventListener("click", () => this.handleRegenerateKey());
  }

  bind2FAEvents() {
    const toggle = document.getElementById("twoFactorToggle");
    if (toggle) {
      toggle.addEventListener("change", async (e) => {
        if (e.target.checked) {
          const response = await fetch("/api/auth/enable-2fa", {
            method: "POST",
            headers: {
              "X-CSRF-TOKEN": document.querySelector('meta[name="csrf-token"]')
                .content,
            },
          });
          if (response.ok) {
            document.getElementById("verificationSection").style.display =
              "block";
            this.showNotification(
              "Verification code sent to your email",
              "success"
            );
          }
        } else {
          const response = await fetch("/api/auth/disable-2fa", {
            method: "POST",
            headers: {
              "X-CSRF-TOKEN": document.querySelector('meta[name="csrf-token"]')
                .content,
            },
          });
          if (response.ok) {
            document.getElementById("verificationSection").style.display =
              "none";
            this.showNotification("2FA disabled successfully", "success");
          }
        }
      });
    }

    document
      .getElementById("verifyCode")
      ?.addEventListener("click", async () => {
        const code = document.getElementById("verificationCode").value;
        const response = await fetch("/api/auth/verify-2fa", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRF-TOKEN": document.querySelector('meta[name="csrf-token"]')
              .content,
          },
          body: JSON.stringify({ code }),
        });
        if (response.ok) {
          document.getElementById("verificationSection").style.display = "none";
          this.showNotification("2FA enabled successfully", "success");
        }
      });
  }

  async handleGenerateKey() {
    try {
      const response = await fetch("/api/user/generate-key", {
        method: "POST",
        headers: {
          "X-CSRF-TOKEN": document.querySelector('meta[name="csrf-token"]')
            .content,
        },
      });

      if (response.ok) {
        this.showNotification("API key generated successfully", "success");
        location.reload();
      } else {
        const data = await response.json();
        throw new Error(data.error || "Failed to generate API key");
      }
    } catch (error) {
      this.logError(error, "API Key Generation");
    }
  }

  async handleRegenerateKey() {
    if (confirm("Are you sure? Current API key will be invalidated.")) {
      await this.handleGenerateKey();
    }
  }

  async loadProfileData() {
    try {
      const response = await fetch("/api/entries/user-stats");
      const data = await response.json();

      const projectCount = document.getElementById("projectCount");
      const entryCount = document.getElementById("entryCount");

      if (projectCount) projectCount.textContent = data.project_count;
      if (entryCount) entryCount.textContent = data.entry_count;

      this.displayRecentEntries(data.entries);
    } catch (error) {
      this.logError(error, "Profile Data Loading");
    }
  }

  displayRecentEntries(entries) {
    const recentEntries = document.getElementById("recentEntries");
    if (!recentEntries) return;

    if (!entries?.length) {
      recentEntries.innerHTML = "<p>No entries yet</p>";
      return;
    }

    recentEntries.innerHTML = entries
      .map(
        (entry) => `
            <div class="card mb-3 entry-preview">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <h5 class="card-title project-name">${
                          entry.project
                        }</h5>
                        <small class="text-muted">${new Date(
                          entry.timestamp
                        ).toLocaleString()}</small>
                    </div>
                    <p class="card-text">${entry.content}</p>
                    ${
                      entry.repository_url
                        ? `
                        <a href="${entry.repository_url}" target="_blank" class="btn btn-sm btn-primary">
                            View Repository
                        </a>
                    `
                        : ""
                    }
                </div>
            </div>
        `
      )
      .join("");
  }
}

class PredictionManager {
  constructor() {
    this.bindEvents();
    // Add logger for debugging
    this.logger = console;
    this.logger.debug("PredictionManager initialized");
  }

  bindEvents() {
    const form = document.getElementById("predictionForm");
    if (form) {
      form.addEventListener("submit", (e) => this.handlePrediction(e));
      this.logger.debug("Form submit event bound");
    }
  }

  sanitizeData(formData) {
    this.logger.debug("Raw form data:", Object.fromEntries(formData));

    // Helper function to ensure numeric values
    const getNumericValue = (value, defaultValue = 0) => {
      return value === null || value === undefined
        ? defaultValue
        : Number(value);
    };

    // Helper function for binary values
    const getBinaryValue = (value, defaultValue = 0) => {
      return value === null || value === undefined
        ? defaultValue
        : Number(value === "yes" || value === "1" || value === true);
    };

    const data = {
      // Basic information
      subject: formData.get("subject") || "mathematics",
      gender: formData.get("gender") || "female",
      sex: Number(formData.get("gender") === "female" ? 0 : 1),
      school: getNumericValue(formData.get("school")),
      age: (getNumericValue(formData.get("age"), 15) - 15) / (22 - 15), // Normalize age
      address: getNumericValue(formData.get("address")),
      famsize: getNumericValue(formData.get("famsize")),
      Pstatus: getNumericValue(formData.get("Pstatus")),
      Medu: getNumericValue(formData.get("Medu")) / 4.0,
      Fedu: getNumericValue(formData.get("Fedu")) / 4.0,
      traveltime: (getNumericValue(formData.get("traveltime"), 1) - 1) / 3.0,
      studytime: (getNumericValue(formData.get("studytime"), 1) - 1) / 3.0,
      failures: getNumericValue(formData.get("failures")) / 4.0,
      schoolsup: getBinaryValue(formData.get("schoolsup")),
      famsup: getBinaryValue(formData.get("famsup")),
      paid: getBinaryValue(formData.get("paid")),
      activities: getBinaryValue(formData.get("activities")),
      nursery: getBinaryValue(formData.get("nursery")),
      higher: getBinaryValue(formData.get("higher")),
      internet: getBinaryValue(formData.get("internet")),
      romantic: getBinaryValue(formData.get("romantic")),
      famrel: (getNumericValue(formData.get("famrel"), 1) - 1) / 4.0,
      freetime: (getNumericValue(formData.get("freetime"), 1) - 1) / 4.0,
      goout: (getNumericValue(formData.get("goout"), 1) - 1) / 4.0,
      Dalc: (getNumericValue(formData.get("Dalc"), 1) - 1) / 4.0,
      Walc: (getNumericValue(formData.get("Walc"), 1) - 1) / 4.0,
      health: (getNumericValue(formData.get("health"), 1) - 1) / 4.0,
      absences: getNumericValue(formData.get("absences")) / 93.0,

      // One-hot encoded job fields
      Mjob_at_home: Number(formData.get("Mjob") === "at_home"),
      Mjob_health: Number(formData.get("Mjob") === "health"),
      Mjob_other: Number(formData.get("Mjob") === "other"),
      Mjob_services: Number(formData.get("Mjob") === "services"),
      Mjob_teacher: Number(formData.get("Mjob") === "teacher"),

      Fjob_at_home: Number(formData.get("Fjob") === "at_home"),
      Fjob_health: Number(formData.get("Fjob") === "health"),
      Fjob_other: Number(formData.get("Fjob") === "other"),
      Fjob_services: Number(formData.get("Fjob") === "services"),
      Fjob_teacher: Number(formData.get("Fjob") === "teacher"),

      // One-hot encoded reason fields
      reason_course: Number(formData.get("reason") === "course"),
      reason_home: Number(formData.get("reason") === "home"),
      reason_other: Number(formData.get("reason") === "other"),
      reason_reputation: Number(formData.get("reason") === "reputation"),

      // One-hot encoded guardian fields
      guardian_father: Number(formData.get("guardian") === "father"),
      guardian_mother: Number(formData.get("guardian") === "mother"),
      guardian_other: Number(formData.get("guardian") === "other"),

      // Calculate Avgalc
      Avgalc:
        (getNumericValue(formData.get("Dalc")) +
          getNumericValue(formData.get("Walc"))) /
        10.0,

      // Calculate Bum score (normalized)
      Bum:
        ((2.0 * getNumericValue(formData.get("failures"))) / 4.0 +
          (1.5 * getNumericValue(formData.get("absences"))) / 93.0 +
          getNumericValue(formData.get("Dalc")) / 5.0 +
          getNumericValue(formData.get("Walc")) / 5.0 +
          (4.0 - getNumericValue(formData.get("studytime"))) / 4.0 +
          (0.5 * getNumericValue(formData.get("freetime"))) / 5.0) /
        6.0,

      // Initialize Gvg as 0
      Gvg: 0.0,
    };

    this.logger.debug("Processed data:", data);
    return this.validateInputs(data);
  }

  async handlePrediction(e) {
    e.preventDefault();
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const resultsDiv = document.getElementById("results");

    try {
      submitBtn.disabled = true;
      const formData = new FormData(form);
      const data = this.sanitizeData(formData);

      this.logger.debug("Sending request with data:", data);

      const response = await fetch("/api/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Prediction failed");
      }

      const result = await response.json();
      this.logger.debug("Received prediction results:", result);

      this.displayResults(result.predictions);
      resultsDiv.style.display = "block";
    } catch (error) {
      this.logger.error("Prediction error:", error);
      showNotification(error.message, "danger");
    } finally {
      submitBtn.disabled = false;
    }
  }

  validateInputs(data) {
    this.logger.debug("Validating inputs:", data);

    // Add validation for all required fields
    const requiredFields = [
      "subject",
      "gender",
      "sex",
      "school",
      "age",
      "address",
      "famsize",
      "Pstatus",
      "Medu",
      "Fedu",
      "traveltime",
      "studytime",
      "failures",
      "schoolsup",
      "famsup",
      "paid",
      "activities",
      "nursery",
      "higher",
      "internet",
      "romantic",
      "famrel",
      "freetime",
      "goout",
      "Dalc",
      "Walc",
      "health",
      "absences",
    ];

    for (const field of requiredFields) {
      if (data[field] === undefined || data[field] === null) {
        this.logger.error(`Missing required field: ${field}`);
        throw new Error(`Missing required field: ${field}`);
      }
    }

    // Validate normalized ranges
    const normalizedFields = {
      age: [0, 1],
      Medu: [0, 1],
      Fedu: [0, 1],
      traveltime: [0, 1],
      studytime: [0, 1],
      failures: [0, 1],
      absences: [0, 1],
      famrel: [0, 1],
      freetime: [0, 1],
      goout: [0, 1],
      Dalc: [0, 1],
      Walc: [0, 1],
      health: [0, 1],
      Avgalc: [0, 1],
      Bum: [0, 1],
    };

    for (const [field, [min, max]] of Object.entries(normalizedFields)) {
      const value = data[field];
      this.logger.debug(`Validating ${field}: ${value}`);
      if (value < min || value > max) {
        this.logger.error(
          `${field} value ${value} outside range [${min}, ${max}]`
        );
        throw new Error(`${field} must be between ${min} and ${max}`);
      }
    }

    return data;
  }

  displayResults(predictions) {
    document.getElementById(
      "g1-prediction"
    ).textContent = `${predictions.G1.toFixed(2)} (${this.getGradeLevel(
      predictions.G1
    )})`;
    document.getElementById(
      "g2-prediction"
    ).textContent = `${predictions.G2.toFixed(2)} (${this.getGradeLevel(
      predictions.G2
    )})`;
    document.getElementById(
      "g3-prediction"
    ).textContent = `${predictions.G3.toFixed(2)} (${this.getGradeLevel(
      predictions.G3
    )})`;
  }

  getGradeLevel(grade) {
    if (grade <= 5) return "Poor";
    if (grade <= 10) return "Below Average";
    if (grade <= 14) return "Average";
    if (grade <= 17) return "Good";
    return "Excellent";
  }
}

// utility functions
function escapeHtml(unsafe) {
  // prevents xss in dynamic stuff
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function showNotification(message, type) {
  // create alert div
  const alert = document.createElement("div");
  alert.className = `alert alert-${
    type === "success" ? "success" : "danger"
  } alert-dismissible fade show`;
  alert.role = "alert";
  alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

  // insert at top of page
  const container = document.querySelector(".container");
  container.insertBefore(alert, container.firstChild);

  // auto remove after 5 seconds
  setTimeout(() => alert.remove(), 5000);
}

// initialize all managers on dom load
document.addEventListener("DOMContentLoaded", () => {
  // Only initialize managers if their respective elements exist
  if (document.getElementById("predictionForm")) {
    new PredictionManager();
  }
  if (window.location.pathname === "/privacy") {
    new PrivacyManager();
  }
  if (window.location.pathname === "/profile") {
    new ProfileManager();
  }
  if (document.getElementById("apiKeySection")) {
    new ProfileManager();
  }
});
