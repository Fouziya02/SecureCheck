/* =========================================================
   SECURECHECK - FRONTEND JAVASCRIPT
   File: static/js/script.js
========================================================= */

(function () {
  "use strict";

  function initializeSecureCheck() {
    const tabButtons = document.querySelectorAll(".tab-button");
    const tabSections = document.querySelectorAll(".tab-content");

    const passwordInput = document.getElementById("password");
    const togglePasswordButton = document.getElementById("togglePassword");

    const liveStrengthBox = document.getElementById("liveStrength");

    const liveStrengthText = document.getElementById("liveStrengthText");

    const liveProgressBar = document.getElementById("liveProgressBar");

    const resultSection = document.getElementById("resultSection");

    /* =====================================
           1. TAB NAVIGATION
        ====================================== */

    function showTab(tabName, clickedButton) {
      const targetSection = document.getElementById(tabName);

      if (!targetSection || !targetSection.classList.contains("tab-content")) {
        console.warn("SecureCheck: tab section not found:", tabName);

        return;
      }

      tabSections.forEach(function (section) {
        section.classList.toggle("active", section === targetSection);
      });

      tabButtons.forEach(function (button) {
        const isSelected =
          button === clickedButton || button.dataset.tab === tabName;

        button.classList.toggle("active", isSelected);

        button.setAttribute("aria-selected", isSelected ? "true" : "false");
      });
    }

    window.showTab = showTab;

    tabButtons.forEach(function (button) {
      const tabName = button.dataset.tab;

      if (tabName) {
        button.addEventListener("click", function () {
          showTab(tabName, button);
        });
      }
    });

    const initiallyActiveSection = document.querySelector(
      ".tab-content.active",
    );

    const initialTabName = initiallyActiveSection
      ? initiallyActiveSection.id
      : "analyzer";

    const initialButton = Array.from(tabButtons).find(function (button) {
      return button.dataset.tab === initialTabName;
    });

    showTab(initialTabName, initialButton || undefined);

    /* =====================================
           2. SHOW / HIDE PASSWORD
        ====================================== */

    if (passwordInput && togglePasswordButton) {
      togglePasswordButton.addEventListener("click", function () {
        const currentlyHidden = passwordInput.type === "password";

        passwordInput.type = currentlyHidden ? "text" : "password";

        togglePasswordButton.setAttribute(
          "aria-label",
          currentlyHidden ? "Hide password" : "Show password",
        );
      });
    }

    /* =====================================
           3. LIVE PASSWORD STRENGTH
        ====================================== */

    const commonPasswords = new Set([
      "password",
      "password123",
      "123456",
      "12345678",
      "123456789",
      "qwerty",
      "qwerty123",
      "admin",
      "admin123",
      "welcome",
      "letmein",
      "iloveyou",
      "abc123",
      "111111",
      "000000",
    ]);

    const predictablePatterns = [
      "123456",
      "654321",
      "abcdef",
      "qwerty",
      "asdf",
      "password",
      "987654",
    ];

    /* INITIAL LIVE INDICATOR: ZERO */

    function setInitialLiveStrength() {
      if (!liveStrengthBox || !liveStrengthText || !liveProgressBar) {
        return;
      }

      liveStrengthBox.hidden = false;

      liveStrengthText.textContent = "0% - Not evaluated";

      liveProgressBar.className = "progress-bar";

      liveProgressBar.style.width = "0%";
    }

    /* LIVE ANALYSIS CALCULATION */

    function analyzePasswordForPreview(password) {
      const lowerPassword = password.toLowerCase();

      const isCommon = commonPasswords.has(lowerPassword);

      const hasPredictablePattern = predictablePatterns.some(
        function (pattern) {
          return lowerPassword.includes(pattern);
        },
      );

      const hasRepeatedCharacters = /(.)\1{2,}/.test(password);

      // Same nine checks as the Flask backend.
      const checks = [
        password.length >= 12,

        password.length >= 16,

        /[A-Z]/.test(password),

        /[a-z]/.test(password),

        /[0-9]/.test(password),

        /[^A-Za-z0-9]/.test(password),

        !isCommon,

        !hasPredictablePattern,

        !hasRepeatedCharacters,
      ];

      const score = checks.filter(Boolean).length;

      const percentage = Math.round((score / checks.length) * 100);

      let strength;

      if (score <= 3) {
        strength = "Weak";
      } else if (score <= 6) {
        strength = "Moderate";
      } else {
        strength = "Strong";
      }

      return {
        strength: strength,
        percentage: percentage,
      };
    }

    /* UPDATE LIVE INDICATOR */

    function updateLiveStrength() {
      if (
        !passwordInput ||
        !liveStrengthBox ||
        !liveStrengthText ||
        !liveProgressBar
      ) {
        return;
      }

      const password = passwordInput.value;

      // Keep initial state at zero.
      if (password.length === 0) {
        setInitialLiveStrength();

        return;
      }

      // Hide previous server result after editing.
      if (resultSection) {
        resultSection.hidden = true;

        resultSection.style.display = "none";
      }

      const result = analyzePasswordForPreview(password);

      liveStrengthBox.hidden = false;

      liveStrengthText.textContent =
        result.strength + " - " + result.percentage + "%";

      liveProgressBar.className =
        "progress-bar strength-bar-" + result.strength.toLowerCase();

      liveProgressBar.style.width = result.percentage + "%";
    }

    if (passwordInput) {
      // Show zero immediately when the page loads.
      setInitialLiveStrength();

      passwordInput.addEventListener("input", updateLiveStrength);
    }

    /* =====================================
           4. SERVER RESULT PROGRESS BAR
        ====================================== */

    const resultProgressBar = document.querySelector(
      "#resultSection .progress-bar[data-percentage]",
    );

    if (resultProgressBar) {
      const percentage = Number(resultProgressBar.dataset.percentage);

      const safePercentage = Number.isFinite(percentage)
        ? Math.min(Math.max(percentage, 0), 100)
        : 0;

      resultProgressBar.style.width = safePercentage + "%";
    }

    /* =====================================
           5. DASHBOARD DISTRIBUTION CHART
        ====================================== */

    const chartContainer = document.getElementById("strengthChart");

    const chartBars = document.querySelectorAll(".chart-bar");

    if (chartContainer && chartBars.length > 0) {
      const totalAnalyzed = Number(chartContainer.dataset.total || 0);

      chartBars.forEach(function (bar) {
        const count = Number(bar.dataset.count || 0);

        const percentage =
          totalAnalyzed > 0 ? (count / totalAnalyzed) * 100 : 0;

        const safePercentage = Math.min(Math.max(percentage, 0), 100);

        bar.style.width = safePercentage + "%";
      });
    }
  }

  // Initialize after the HTML has loaded.
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeSecureCheck, {
      once: true,
    });
  } else {
    initializeSecureCheck();
  }
})();
