/**
 * Applicant Tracking System (ATS) - Frontend Interactions
 * Beginner-friendly JavaScript for file drag-and-drop, instant search filtering, and UX enhancements.
 */

document.addEventListener("DOMContentLoaded", function () {
    // -------------------------------------------------------------------------
    // 1. Drag and Drop File Upload Handler
    // -------------------------------------------------------------------------
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("resume_file");
    const fileNamePreview = document.getElementById("file-name-preview");

    if (dropzone && fileInput) {
        // Highlight dropzone on dragover
        ["dragenter", "dragover"].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add("dragover");
            }, false);
        });

        // Remove highlight on dragleave or drop
        ["dragleave", "drop"].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove("dragover");
            }, false);
        });

        // Handle file dropped into dropzone
        dropzone.addEventListener("drop", (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                updateFileNameDisplay(files[0].name);
            }
        });

        // Handle regular file input change (when user clicks and selects file)
        fileInput.addEventListener("change", function () {
            if (this.files && this.files.length > 0) {
                updateFileNameDisplay(this.files[0].name);
            }
        });

        function updateFileNameDisplay(name) {
            if (fileNamePreview) {
                fileNamePreview.textContent = `Selected: ${name}`;
                fileNamePreview.classList.remove("hidden");
            }
        }
    }

    // -------------------------------------------------------------------------
    // 2. Client-side Real-time Search & Filter for Candidates Table
    // -------------------------------------------------------------------------
    const searchInput = document.getElementById("search");
    const statusSelect = document.getElementById("status");
    const candidatesTable = document.getElementById("candidatesTable");

    if (candidatesTable && searchInput) {
        const rows = candidatesTable.querySelectorAll("tbody tr[data-name]");

        function filterRows() {
            const query = searchInput.value.trim().toLowerCase();
            const statusFilter = statusSelect ? statusSelect.value : "All";

            let visibleCount = 0;

            rows.forEach(row => {
                const name = row.getAttribute("data-name") || "";
                const skills = row.getAttribute("data-skills") || "";
                const missing = row.getAttribute("data-missing") || "";
                const rowStatus = row.getAttribute("data-status") || "";

                const matchesQuery = query === "" || 
                                     name.includes(query) || 
                                     skills.includes(query) || 
                                     missing.includes(query);
                const matchesStatus = statusFilter === "All" || rowStatus === statusFilter;

                if (matchesQuery && matchesStatus) {
                    row.style.display = "";
                    visibleCount++;
                } else {
                    row.style.display = "none";
                }
            });
        }

        // Live filter as recruiter types in the search bar
        searchInput.addEventListener("input", filterRows);
    }

    // -------------------------------------------------------------------------
    // 3. Status Select Styling Feedback
    // -------------------------------------------------------------------------
    const statusSelects = document.querySelectorAll(".status-select");
    statusSelects.forEach(select => {
        select.addEventListener("change", function () {
            // Remove previous classes
            this.classList.remove("status-select-reviewing", "status-select-shortlisted", "status-select-rejected");
            // Add matching status class
            this.classList.add(`status-select-${this.value.toLowerCase()}`);
        });
    });

    // -------------------------------------------------------------------------
    // 4. Auto-dismiss Flash Alerts
    // -------------------------------------------------------------------------
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = "0";
            alert.style.transition = "opacity 0.5s ease";
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});

// -------------------------------------------------------------------------
// 5. Copy Candidate Feedback to Clipboard Functions
// -------------------------------------------------------------------------
window.copyFeedbackText = function (elementId, buttonElem) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const text = el.innerText || el.textContent;

    navigator.clipboard.writeText(text).then(() => {
        const toast = document.getElementById("copyToast");
        if (toast) {
            toast.classList.add("show");
            setTimeout(() => toast.classList.remove("show"), 3000);
        } else if (buttonElem) {
            const originalText = buttonElem.innerHTML;
            buttonElem.innerHTML = "✓ Copied Feedback!";
            setTimeout(() => { buttonElem.innerHTML = originalText; }, 2500);
        }
    }).catch(err => {
        console.error("Failed to copy text: ", err);
    });
};

window.copyCandidateFeedbackQuick = function (candidateId, buttonElem) {
    buttonElem.style.opacity = "0.5";
    fetch(`/api/candidate/${candidateId}/feedback`)
        .then(res => res.json())
        .then(data => {
            buttonElem.style.opacity = "1";
            if (data.success && data.feedback) {
                navigator.clipboard.writeText(data.feedback).then(() => {
                    const originalTitle = buttonElem.getAttribute("title");
                    buttonElem.setAttribute("title", "Copied feedback email to clipboard!");
                    buttonElem.classList.add("btn-green-active");
                    setTimeout(() => {
                        buttonElem.setAttribute("title", originalTitle);
                        buttonElem.classList.remove("btn-green-active");
                    }, 2500);
                });
            }
        })
        .catch(err => {
            buttonElem.style.opacity = "1";
            console.error("Error fetching feedback:", err);
        });
};
