document.addEventListener("DOMContentLoaded", () => {

    // =====================================
    // ELEMENT REFERENCES
    // =====================================

    const fileInput = document.getElementById("fileInput");
    const uploadTrigger = document.getElementById("uploadTrigger");
    const browseFiles = document.getElementById("browseFiles");
    const emptyUploadTrigger = document.getElementById("emptyUploadTrigger");

    const uploadArea = document.getElementById("uploadArea");
    const uploadStatus = document.getElementById("uploadStatus");
    const filesLoading = document.getElementById("filesLoading");
    const filesList = document.getElementById("filesList");
    const fileCount = document.getElementById("fileCount");

    const memorySearch = document.getElementById("memorySearch");
    const searchButton = document.getElementById("searchButton");

    const viewAllFiles = document.getElementById("viewAllFiles");
    const filesHeading = document.getElementById("filesHeading");

    const searchResults = document.getElementById("searchResults");
    const searchResultsList = document.getElementById("searchResultsList");
    const searchResultCount = document.getElementById("searchResultCount");
    const searchLoading = document.getElementById("searchLoading");

    // =====================================
    // APPLICATION STATE
    // =====================================

    let uploadedFiles = [];
    let activeFilter = "all";
    let searchDebounceTimer = null;

    // =====================================
    // UTILITY HELPERS
    // =====================================

    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function highlightHtml(text, terms) {
        if (!text) return "";
        let escaped = escapeHtml(text);
        if (!terms || !terms.length) return escaped;

        terms.forEach(term => {
            if (!term || term.length < 2) return;
            const regex = new RegExp(`(${term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");
            escaped = escaped.replace(regex, "<mark>$1</mark>");
        });

        return escaped;
    }

    function getFileType(filename) {
        const ext = (filename || "").split(".").pop().toLowerCase();
        if (["png", "jpg", "jpeg"].includes(ext)) {
            return "image";
        }
        if (["pdf", "docx", "txt", "md"].includes(ext)) {
            return "document";
        }
        return "other";
    }

    function getFileIcon(filename) {
        const ext = (filename || "").split(".").pop().toLowerCase();
        if (ext === "pdf") return "📄";
        if (ext === "docx" || ext === "doc") return "📝";
        if (ext === "txt" || ext === "md") return "📋";
        if (["png", "jpg", "jpeg"].includes(ext)) return "🖼️";
        return "▤";
    }

    function formatSize(bytes) {
        if (!bytes || bytes <= 0) return "0 B";
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    }

    // =====================================
    // FILE PICKER
    // =====================================

    function openFilePicker() {
        if (fileInput) fileInput.click();
    }

    [uploadTrigger, browseFiles, emptyUploadTrigger].forEach(button => {
        if (button) {
            button.addEventListener("click", openFilePicker);
        }
    });

    // =====================================
    // FILE UPLOAD & INDEXING
    // =====================================

    async function uploadFiles(files) {
        if (!files || !files.length) return;

        const formData = new FormData();
        Array.from(files).forEach(file => {
            formData.append("files", file);
        });

        if (uploadStatus) {
            uploadStatus.textContent = "Processing documents, extracting text & indexing...";
            uploadStatus.style.color = "var(--workspace-purple)";
        }

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });

            const result = await response.json();

            if (!response.ok && response.status !== 207) {
                throw new Error(result.error || "Upload failed.");
            }

            const errors = result.errors || [];
            let statusMessage = result.message || "Upload completed.";
            if (errors.length) {
                statusMessage += " (" + errors.join(" | ") + ")";
            }

            if (uploadStatus) {
                uploadStatus.textContent = statusMessage;
                uploadStatus.style.color = errors.length && !result.files?.length ? "#f87171" : "#34d399";
            }

            await loadFiles();

            // If user has an active search, re-run search against newly indexed docs
            const currentQuery = memorySearch ? memorySearch.value.trim() : "";
            if (currentQuery) {
                performSearch(currentQuery);
            }

        } catch (error) {
            console.error("Upload error:", error);
            if (uploadStatus) {
                uploadStatus.textContent = error.message;
                uploadStatus.style.color = "#f87171";
            }
        } finally {
            if (fileInput) fileInput.value = "";
        }
    }

    if (fileInput) {
        fileInput.addEventListener("change", event => {
            uploadFiles(event.target.files);
        });
    }

    // =====================================
    // DRAG AND DROP
    // =====================================

    if (uploadArea) {
        ["dragenter", "dragover"].forEach(eventName => {
            uploadArea.addEventListener(eventName, event => {
                event.preventDefault();
                uploadArea.classList.add("drag-over");
            });
        });

        ["dragleave", "drop"].forEach(eventName => {
            uploadArea.addEventListener(eventName, event => {
                event.preventDefault();
                uploadArea.classList.remove("drag-over");
            });
        });

        uploadArea.addEventListener("drop", event => {
            uploadFiles(event.dataTransfer.files);
        });
    }

    // =====================================
    // NATURAL LANGUAGE SEARCH & EXPLAINABILITY
    // =====================================

    async function performSearch(query) {
        const cleanQuery = (query || "").trim();

        if (!cleanQuery) {
            if (searchResults) searchResults.hidden = true;
            return;
        }

        if (searchResults) searchResults.hidden = false;
        if (searchLoading) searchLoading.style.display = "block";
        if (searchResultCount) searchResultCount.textContent = "Analyzing memory...";
        if (searchResultsList) searchResultsList.innerHTML = "";

        try {
            const response = await fetch(`/search?q=${encodeURIComponent(cleanQuery)}`);
            if (!response.ok) {
                throw new Error("Search service unavailable.");
            }

            const data = await response.json();
            const results = data.results || [];

            if (searchResultCount) {
                searchResultCount.textContent = `${results.length} ${results.length === 1 ? "match found" : "matches found"}`;
            }

            if (!searchResultsList) return;
            searchResultsList.innerHTML = "";

            if (!results.length) {
                searchResultsList.innerHTML = `
                    <div class="search-no-results">
                        No matching documents found in your memory for "${escapeHtml(cleanQuery)}".<br>
                        <small style="color:var(--workspace-muted);margin-top:6px;display:inline-block;">
                            Try describing key subjects, document contents, or upload relevant files.
                        </small>
                    </div>
                `;
                return;
            }

            results.forEach(res => {
                const item = document.createElement("div");
                item.className = "search-result-item";

                const thumbnail = document.createElement("div");
                thumbnail.className = "search-result-thumbnail";

                const type = getFileType(res.document_name);
                if (type === "image") {
                    const img = document.createElement("img");
                    img.src = `/preview/${encodeURIComponent(res.stored_name)}`;
                    img.alt = res.document_name;
                    thumbnail.appendChild(img);
                } else {
                    thumbnail.textContent = getFileIcon(res.document_name);
                }

                const info = document.createElement("div");
                info.className = "search-result-info";

                // Header with name and score badge
                const header = document.createElement("div");
                header.className = "search-result-header";

                const name = document.createElement("strong");
                name.textContent = res.document_name;

                const scoreBadge = document.createElement("span");
                const searchType = res.search_type || "semantic";
                scoreBadge.className = `search-badge ${searchType}`;
                scoreBadge.innerHTML = `
                    <span class="search-result-score">${res.relevance_score}%</span>
                    <span>${searchType.toUpperCase()}</span>
                `;

                header.append(name, scoreBadge);

                // Details
                const details = document.createElement("small");
                details.textContent = `${(res.file_type || type).toUpperCase()} · ${formatSize(res.size || 0)}`;

                // Snippet with matching keywords highlighted
                const snippet = document.createElement("div");
                snippet.className = "search-result-snippet";
                snippet.innerHTML = highlightHtml(res.matching_content, res.matched_terms);

                // Explainability box
                const explanation = document.createElement("div");
                explanation.className = "search-result-explanation";
                explanation.innerHTML = `
                    <span class="explanation-icon">💡</span>
                    <span><strong>Why this matched:</strong> ${escapeHtml(res.reason)}</span>
                `;

                info.append(header, details, snippet, explanation);

                // Preview button
                const previewButton = document.createElement("button");
                previewButton.className = "search-result-preview";
                previewButton.textContent = "Preview Memory";
                previewButton.addEventListener("click", () => {
                    window.open(
                        `/preview/${encodeURIComponent(res.stored_name)}`,
                        "_blank",
                        "noopener"
                    );
                });

                item.append(thumbnail, info, previewButton);
                searchResultsList.appendChild(item);
            });

        } catch (error) {
            console.error("Search error:", error);
            if (searchResultsList) {
                searchResultsList.innerHTML = `
                    <div class="search-no-results" style="color:#f87171;">
                        Search request error: ${escapeHtml(error.message)}
                    </div>
                `;
            }
        } finally {
            if (searchLoading) searchLoading.style.display = "none";
        }
    }

    // =====================================
    // MEMORY LIBRARY RENDERING
    // =====================================

    function getFilteredFiles() {
        let files = [...uploadedFiles];

        if (activeFilter === "image") {
            files = files.filter(f => getFileType(f.name) === "image");
        } else if (activeFilter === "document") {
            files = files.filter(f => getFileType(f.name) === "document");
        } else if (activeFilter === "recent") {
            files.reverse();
            files = files.slice(0, 5);
        }

        return files;
    }

    function renderFiles() {
        const filteredFiles = getFilteredFiles();

        if (fileCount) {
            fileCount.textContent = `${uploadedFiles.length} ${
                uploadedFiles.length === 1 ? "file" : "files"
            }`;
        }

        if (!filesList) return;
        filesList.innerHTML = "";

        if (!filteredFiles.length) {
            filesList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">✧</div>
                    <h3>No files in this section</h3>
                    <p>Upload a PDF, DOCX or TXT document to begin your memory library.</p>
                </div>
            `;
            return;
        }

        filteredFiles.forEach(file => {
            const type = getFileType(file.name);
            const icon = getFileIcon(file.name);

            const row = document.createElement("div");
            row.className = "file-row";

            const iconBox = document.createElement("div");
            iconBox.className = "file-type-icon";
            iconBox.textContent = icon;

            const info = document.createElement("div");
            info.className = "file-row-info";

            const name = document.createElement("strong");
            name.textContent = file.name;

            const details = document.createElement("small");
            const wordMeta = file.word_count ? ` · ${file.word_count} words` : "";
            const privacyMeta = file.privacy_protected ? " · 🔒 Privacy Processed" : "";
            details.textContent = `${(file.extension || type).toUpperCase()} · ${formatSize(file.size || 0)}${wordMeta}${privacyMeta}`;

            info.append(name, details);

            const actions = document.createElement("div");
            actions.className = "file-actions";

            const previewButton = document.createElement("button");
            previewButton.className = "file-action-button";
            previewButton.textContent = "Preview";
            previewButton.addEventListener("click", () => {
                window.open(
                    `/preview/${encodeURIComponent(file.stored_name)}`,
                    "_blank",
                    "noopener"
                );
            });

            const deleteButton = document.createElement("button");
            deleteButton.className = "file-action-button delete-action";
            deleteButton.textContent = "Delete";
            deleteButton.addEventListener("click", () => {
                deleteFile(file);
            });

            actions.append(previewButton, deleteButton);
            row.append(iconBox, info, actions);
            filesList.appendChild(row);
        });
    }

    // =====================================
    // LOAD FILES FROM FLASK
    // =====================================

    async function loadFiles() {
        if (filesLoading) filesLoading.style.display = "block";
        if (filesList) filesList.style.display = "none";

        try {
            const response = await fetch("/files");
            if (!response.ok) {
                throw new Error("Could not load your saved memories.");
            }

            const result = await response.json();
            uploadedFiles = result.files || [];
            renderFiles();

        } catch (error) {
            console.error("File loading error:", error);
            if (uploadStatus) {
                uploadStatus.textContent = error.message;
            }
        } finally {
            if (filesLoading) filesLoading.style.display = "none";
            if (filesList) filesList.style.display = "";
        }
    }

    // =====================================
    // DELETE FILE
    // =====================================

    async function deleteFile(file) {
        const confirmed = confirm(
            `Are you sure you want to delete "${file.name}" from your RecallQ memory?`
        );
        if (!confirmed) return;

        try {
            const response = await fetch(
                `/delete/${encodeURIComponent(file.stored_name)}`,
                { method: "DELETE" }
            );

            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.error || "Could not delete file.");
            }

            if (uploadStatus) {
                uploadStatus.textContent = result.message;
                uploadStatus.style.color = "#34d399";
            }

            await loadFiles();

            // Re-run search if active
            const currentQuery = memorySearch ? memorySearch.value.trim() : "";
            if (currentQuery) {
                performSearch(currentQuery);
            }

        } catch (error) {
            console.error("Delete error:", error);
            if (uploadStatus) {
                uploadStatus.textContent = error.message;
                uploadStatus.style.color = "#f87171";
            }
        }
    }

    // =====================================
    // SEARCH EVENT LISTENERS
    // =====================================

    if (searchButton && memorySearch) {
        searchButton.addEventListener("click", () => {
            performSearch(memorySearch.value);
        });
    }

    if (memorySearch) {
        memorySearch.addEventListener("input", () => {
            clearTimeout(searchDebounceTimer);
            const query = memorySearch.value.trim();
            if (!query) {
                if (searchResults) searchResults.hidden = true;
                return;
            }
            searchDebounceTimer = setTimeout(() => {
                performSearch(query);
            }, 300);
        });

        memorySearch.addEventListener("keydown", event => {
            if (event.key === "Enter") {
                event.preventDefault();
                clearTimeout(searchDebounceTimer);
                performSearch(memorySearch.value);
            }
        });
    }

    // Quick search suggestions
    document.querySelectorAll(".suggestion").forEach(button => {
        button.addEventListener("click", () => {
            const term = button.textContent.trim();
            if (memorySearch) {
                memorySearch.value = term;
            }
            performSearch(term);
        });
    });

    // =====================================
    // NAVIGATION & CATEGORY FILTERS
    // =====================================

    function updateActiveNavigation() {
        document.querySelectorAll("[data-filter]").forEach(item => {
            item.classList.toggle(
                "active",
                item.dataset.filter === activeFilter
            );
        });
    }

    document.querySelectorAll("[data-filter]").forEach(button => {
        button.addEventListener("click", event => {
            event.preventDefault();
            activeFilter = button.dataset.filter;

            if (filesHeading) {
                if (activeFilter === "all") filesHeading.textContent = "All Memories";
                else if (activeFilter === "image") filesHeading.textContent = "Images";
                else if (activeFilter === "document") filesHeading.textContent = "Documents";
                else if (activeFilter === "recent") filesHeading.textContent = "Recently Added";
            }

            updateActiveNavigation();
            renderFiles();
        });
    });

    if (viewAllFiles) {
        viewAllFiles.addEventListener("click", () => {
            activeFilter = "all";
            if (filesHeading) filesHeading.textContent = "All Memories";
            updateActiveNavigation();
            renderFiles();
        });
    }

    // =====================================
    // INITIALIZATION
    // =====================================

    updateActiveNavigation();
    loadFiles();
});
