(() => {
  "use strict";

  const API_BASE_URL = "";
  const API_ENDPOINTS = {
    query: "/api/query",
    upload: "/api/upload",
    documents: "/api/documents",
  };
  const SESSION_STORAGE_KEY = "pdf-ai-assistant-session-id";
  const TOP_K = 5;

  const state = {
    sessionId: "",
    isSearching: false,
    documents: [],
    turns: [],
  };

  const elements = {};

  document.addEventListener("DOMContentLoaded", initializeApp);

  async function initializeApp() {
    cacheElements();
    state.sessionId = getOrCreateSessionId();
    bindEvents();
    await loadDocuments();
  }

  function cacheElements() {
    const ids = [
      "search-form",
      "query-input",
      "search-button",
      "loading-state",
      "welcome-state",
      "results-stack",
      "global-error",
      "global-error-message",
      "dismiss-error",
      "upload-zone",
      "pdf-input",
      "browse-button",
      "upload-status",
      "upload-progress",
      "upload-progress-bar",
      "document-list",
      "document-count",
      "refresh-documents-button",
      "new-conversation-button",
      "documents-panel",
      "documents-toggle",
      "toast",
    ];

    ids.forEach((id) => {
      elements[id] = document.getElementById(id);
    });
  }

  function bindEvents() {
    elements["search-form"].addEventListener("submit", (event) => {
      event.preventDefault();
      submitQuery();
    });

    elements["query-input"].addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        submitQuery();
      }
    });

    elements["dismiss-error"].addEventListener("click", hideError);
    elements["refresh-documents-button"].addEventListener("click", loadDocuments);
    elements["new-conversation-button"].addEventListener("click", startNewConversation);
    elements["browse-button"].addEventListener("click", () => elements["pdf-input"].click());
    elements["pdf-input"].addEventListener("change", handleFileSelection);
    elements["documents-toggle"].addEventListener("click", toggleDocumentsPanel);

    elements["upload-zone"].addEventListener("click", (event) => {
      if (event.target.closest("button")) return;
      elements["pdf-input"].click();
    });

    elements["upload-zone"].addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        elements["pdf-input"].click();
      }
    });

    ["dragenter", "dragover"].forEach((eventName) => {
      elements["upload-zone"].addEventListener(eventName, handleDragOver);
    });
    ["dragleave", "drop"].forEach((eventName) => {
      elements["upload-zone"].addEventListener(eventName, handleDragLeave);
    });
    elements["upload-zone"].addEventListener("drop", handleDrop);
  }

  function generateSessionId() {
    if (window.crypto && typeof window.crypto.randomUUID === "function") {
      return window.crypto.randomUUID();
    }
    return `session-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
  }

  function getOrCreateSessionId() {
    try {
      const savedSessionId = window.sessionStorage.getItem(SESSION_STORAGE_KEY);
      if (savedSessionId) return savedSessionId;

      const sessionId = generateSessionId();
      window.sessionStorage.setItem(SESSION_STORAGE_KEY, sessionId);
      return sessionId;
    } catch (_error) {
      return generateSessionId();
    }
  }

  async function submitQuery() {
    if (state.isSearching) return;

    const query = elements["query-input"].value.trim();
    if (!query) {
      showError("Please enter a question before sending.");
      elements["query-input"].focus();
      return;
    }

    hideError();
    elements["query-input"].value = "";
    elements["welcome-state"].hidden = true;

    // Append User Message to Chat Thread
    const turnId = `turn-${Date.now()}`;
    appendUserMessage(query);
    showLoading();

    try {
      const response = await queryAPI(query);
      state.turns.push({ id: turnId, query, response });
      renderChatbotTurn(turnId, query, response);
    } catch (error) {
      showError(getUserFriendlyError(error, "We couldn't process your question right now."));
    } finally {
      hideLoading();
    }
  }

  async function queryAPI(query) {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.query}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        query,
        session_id: state.sessionId,
        top_k: TOP_K,
      }),
    });

    if (!response.ok) {
      throw new Error(`QUERY_HTTP_${response.status}`);
    }

    let payload;
    try {
      payload = await response.json();
    } catch (_error) {
      throw new Error("QUERY_INVALID_JSON");
    }

    if (!isValidQueryResponse(payload)) {
      throw new Error("QUERY_INVALID_RESPONSE");
    }

    return payload;
  }

  function isValidQueryResponse(payload) {
    return Boolean(
      payload &&
        typeof payload === "object" &&
        payload.chatbot &&
        typeof payload.chatbot === "object",
    );
  }

  function appendUserMessage(queryText) {
    const userDiv = document.createElement("div");
    userDiv.className = "chat-user-message";
    userDiv.innerHTML = `
      <div class="user-avatar" aria-hidden="true">You</div>
      <div class="user-bubble"><p>${escapeHTML(queryText)}</p></div>
    `;
    elements["results-stack"].appendChild(userDiv);
    userDiv.scrollIntoView({ behavior: "smooth", block: "end" });
  }

  function renderChatbotTurn(turnId, queryText, response) {
    const turnContainer = document.createElement("div");
    turnContainer.className = "chat-turn-container";
    turnContainer.id = turnId;

    const chatbotData = response.chatbot || {};
    const answer = typeof chatbotData.answer === "string" ? chatbotData.answer.trim() : "";
    const sources = Array.isArray(chatbotData.sources) ? chatbotData.sources : [];

    const chatbotHTML = `
      <article class="answer-card result-card chatbot-top-layer">
        <div class="result-card-header">
          <div class="section-title">
            <span class="section-icon answer-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path d="M12 3a8 8 0 0 0-5 14.25V20h10v-2.75A8 8 0 0 0 12 3Z" />
                <path d="M9 23h6M9 13h6M10 10h4" />
              </svg>
            </span>
            <div>
              <p class="eyebrow">Interactive AI Chatbot</p>
              <h2>Chatbot Response</h2>
            </div>
          </div>
          <button class="button button-quiet button-small copy-btn" type="button" data-turn-id="${turnId}">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <rect x="8" y="8" width="11" height="12" rx="2" />
              <path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h2" />
            </svg>
            <span>Copy</span>
          </button>
        </div>
        <div class="answer-content">${answer ? renderBasicMarkdown(answer) : '<p class="no-results">No AI answer was returned for this question.</p>'}</div>
        
        ${
          sources.length > 0
            ? `
          <div class="source-divider"></div>
          <div class="sources-block">
            <div class="subsection-heading">
              <h3>Sources Referenced (${sources.length})</h3>
            </div>
            <div class="source-list">
              ${sources
                .map((src) => {
                  const fn = escapeHTML(src.filename || "Document");
                  const loc = formatLocation(src);
                  return `<div class="source-chip"><strong>${fn}</strong>${loc ? ` — ${escapeHTML(loc)}` : ""}</div>`;
                })
                .join("")}
            </div>
          </div>`
            : ""
        }
      </article>
    `;

    turnContainer.innerHTML = chatbotHTML;
    elements["results-stack"].appendChild(turnContainer);

    const copyBtn = turnContainer.querySelector(".copy-btn");
    if (copyBtn) {
      copyBtn.addEventListener("click", () => copyText(answer));
    }

    turnContainer.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderBasicMarkdown(markdown) {
    const escaped = escapeHTML(markdown);
    return escaped
      .split(/\n{2,}/)
      .map((paragraph) => {
        let formatted = paragraph.replace(/\n/g, "<br />");
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
        formatted = formatted.replace(/`(.+?)`/g, "<code>$1</code>");
        return `<p>${formatted}</p>`;
      })
      .join("");
  }

  async function uploadPDF(file) {
    if (!file) return;
    if (!isPDF(file)) {
      setUploadStatus("Only PDF files are accepted.", "error");
      return;
    }

    hideError();
    setUploadStatus(`Uploading ${file.name}...`);
    elements["upload-zone"].classList.add("is-uploading");
    elements["upload-progress"].hidden = false;
    elements["upload-progress-bar"].style.width = "0%";

    try {
      await uploadWithProgress(file);
      setUploadStatus("Upload complete. Document added to library.", "success");
      showToast("PDF uploaded successfully.");
      await loadDocuments();
    } catch (error) {
      setUploadStatus(getUserFriendlyError(error, "The PDF could not be uploaded."), "error");
    } finally {
      elements["upload-zone"].classList.remove("is-uploading");
      elements["upload-progress"].hidden = true;
      elements["pdf-input"].value = "";
    }
  }

  function uploadWithProgress(file) {
    return new Promise((resolve, reject) => {
      const request = new XMLHttpRequest();
      request.open("POST", `${API_BASE_URL}${API_ENDPOINTS.upload}`);
      request.responseType = "json";

      request.upload.addEventListener("progress", (event) => {
        if (!event.lengthComputable) return;
        elements["upload-progress-bar"].style.width = `${Math.round((event.loaded / event.total) * 100)}%`;
      });

      request.addEventListener("load", () => {
        if (request.status >= 200 && request.status < 300) {
          resolve(request.response);
        } else {
          reject(new Error(`UPLOAD_HTTP_${request.status}`));
        }
      });
      request.addEventListener("error", () => reject(new Error("NETWORK_ERROR")));
      request.addEventListener("abort", () => reject(new Error("UPLOAD_ABORTED")));

      const formData = new FormData();
      formData.append("file", file);
      request.send(formData);
    });
  }

  async function loadDocuments() {
    try {
      const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.documents}`, {
        headers: { Accept: "application/json" },
      });

      if (!response.ok) throw new Error(`DOCUMENTS_HTTP_${response.status}`);
      const payload = await response.json();
      state.documents = normalizeDocuments(payload);
      renderDocuments(state.documents);
    } catch (error) {
      renderDocuments([]);
      showError(getUserFriendlyError(error, "We couldn't load your document library."));
    }
  }

  function normalizeDocuments(payload) {
    if (Array.isArray(payload)) return payload;
    if (payload && Array.isArray(payload.documents)) return payload.documents;
    if (payload && Array.isArray(payload.results)) return payload.results;
    return [];
  }

  function renderDocuments(documents) {
    const count = documents.length;
    elements["document-count"].textContent = `${count} document${count === 1 ? "" : "s"}`;

    if (!count) {
      elements["document-list"].innerHTML = `
        <div class="empty-library">
          <span class="empty-library-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21.5zM4 5.5v16M8 7h8M8 11h8" /></svg>
          </span>
          <p>No PDFs yet</p>
          <span>Upload a document to start asking questions.</span>
        </div>
      `;
      return;
    }

    elements["document-list"].innerHTML = documents
      .map((document) => {
        const id = document.id ?? document.document_id ?? document.documentId;
        const status = String(document.status || "ready").toLowerCase();
        const statusLabel = status === "completed" ? "Ready" : capitalize(status);
        const name = escapeHTML(document.filename || document.name || "Untitled document");
        return `
          <div class="document-item">
            <span class="document-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24"><path d="M6 3h8l4 4v14H6zM14 3v5h4M9 12h6M9 16h6" /></svg>
            </span>
            <div class="document-meta">
              <span class="document-name" title="${name}">${name}</span>
              <span class="document-status ${escapeHTML(status)}">${escapeHTML(statusLabel)}</span>
            </div>
            <div class="document-actions">
              <button class="delete-document" type="button" data-document-id="${escapeHTML(id)}" aria-label="Delete ${name}">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M10 11v6M14 11v6M6 7l1 14h10l1-14M9 7V4h6v3" /></svg>
              </button>
            </div>
          </div>
        `;
      })
      .join("");

    elements["document-list"].querySelectorAll(".delete-document").forEach((button) => {
      button.addEventListener("click", () => deleteDocument(button.dataset.documentId));
    });
  }

  async function deleteDocument(documentId) {
    if (!documentId) return;
    if (!window.confirm("Delete this PDF from your library?")) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}${API_ENDPOINTS.documents}/${encodeURIComponent(documentId)}`,
        { method: "DELETE", headers: { Accept: "application/json" } },
      );
      if (!response.ok) throw new Error(`DELETE_HTTP_${response.status}`);
      showToast("Document deleted.");
      await loadDocuments();
    } catch (error) {
      showError(getUserFriendlyError(error, "The document could not be deleted."));
    }
  }

  function showLoading() {
    state.isSearching = true;
    elements["loading-state"].hidden = false;
    elements["search-button"].disabled = true;
    elements["query-input"].disabled = true;
    elements["search-button"].querySelector("span").textContent = "Thinking...";
  }

  function hideLoading() {
    state.isSearching = false;
    elements["loading-state"].hidden = true;
    elements["search-button"].disabled = false;
    elements["query-input"].disabled = false;
    elements["search-button"].querySelector("span").textContent = "Send Message";
  }

  function showError(message) {
    elements["global-error-message"].textContent = message;
    elements["global-error"].hidden = false;
  }

  function hideError() {
    elements["global-error"].hidden = true;
    elements["global-error-message"].textContent = "";
  }

  function handleFileSelection(event) {
    const [file] = event.target.files || [];
    uploadPDF(file);
  }

  function handleDragOver(event) {
    event.preventDefault();
    elements["upload-zone"].classList.add("drag-over");
  }

  function handleDragLeave(event) {
    event.preventDefault();
    elements["upload-zone"].classList.remove("drag-over");
  }

  function handleDrop(event) {
    event.preventDefault();
    elements["upload-zone"].classList.remove("drag-over");
    const [file] = event.dataTransfer.files || [];
    uploadPDF(file);
  }

  function setUploadStatus(message, type = "") {
    elements["upload-status"].textContent = message;
    elements["upload-status"].className = `upload-status ${type}`.trim();
  }

  function isPDF(file) {
    return file && (file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf"));
  }

  function startNewConversation() {
    state.sessionId = generateSessionId();
    state.turns = [];
    try {
      window.sessionStorage.setItem(SESSION_STORAGE_KEY, state.sessionId);
    } catch (_error) {}

    elements["query-input"].value = "";
    elements["results-stack"].innerHTML = `
      <div class="welcome-state" id="welcome-state">
        <div class="welcome-art" aria-hidden="true">
          <span class="welcome-orb orb-one"></span>
          <span class="welcome-orb orb-two"></span>
          <span class="welcome-orb orb-three"></span>
          <svg viewBox="0 0 80 80">
            <path d="M24 16h25l10 10v38H24z" />
            <path d="M49 16v12h10M32 42h19M32 50h13M32 34h8" />
            <circle cx="56" cy="59" r="11" />
            <path d="m64 67 7 7" />
          </svg>
        </div>
        <h3>Your AI Chatbot is ready.</h3>
        <p>Upload a PDF document and type a question to start an interactive chat session with source references.</p>
      </div>
    `;
    cacheElements();
    hideError();
    showToast("Started a new conversation session.");
    elements["query-input"].focus();
  }

  function toggleDocumentsPanel() {
    const isCollapsed = elements["documents-panel"].classList.toggle("collapsed");
    elements["documents-toggle"].setAttribute("aria-expanded", String(!isCollapsed));
    elements["documents-toggle"].setAttribute(
      "aria-label",
      isCollapsed ? "Expand document library" : "Collapse document library",
    );
  }

  async function copyText(text) {
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      showToast("Response copied to clipboard.");
    } catch (_error) {
      showToast("Copy is unavailable in this browser.");
    }
  }

  function showToast(message) {
    elements["toast"].textContent = message;
    elements["toast"].hidden = false;
    window.clearTimeout(showToast.timeoutId);
    showToast.timeoutId = window.setTimeout(() => {
      elements["toast"].hidden = true;
    }, 2800);
  }

  function formatLocation(item) {
    const parts = [];
    if (item.page_number !== undefined && item.page_number !== null) {
      parts.push(`Page ${item.page_number}`);
    }
    if (item.paragraph_number !== undefined && item.paragraph_number !== null) {
      parts.push(`Paragraph ${item.paragraph_number}`);
    }
    return parts.join(" · ");
  }

  function capitalize(value) {
    return value ? value.charAt(0).toUpperCase() + value.slice(1) : "Ready";
  }

  function escapeHTML(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function getUserFriendlyError(error, fallback) {
    const code = error instanceof Error ? error.message : "";
    if (code === "NETWORK_ERROR" || code === "QUERY_HTTP_0" || code === "DOCUMENTS_HTTP_0") {
      return "We couldn't reach the backend chatbot service. Check your connection.";
    }
    if (code.includes("HTTP_404")) return "The chatbot endpoint was not found.";
    if (code.includes("HTTP_413")) return "This PDF file is too large.";
    if (code.includes("HTTP_415")) return "Only PDF files are accepted.";
    return fallback;
  }
})();