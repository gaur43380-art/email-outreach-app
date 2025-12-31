// templates.js

// Save template
async function saveTemplate() {
    const template = document.getElementById("emailTemplate").value;
    
    if (!template.trim()) {
        showStatus("Template cannot be empty!", "error");
        return;
    }

    try {
        const response = await fetch("/templates/save", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ template: template })
        });

        const result = await response.json();

        if (response.ok) {
            showStatus("Template saved successfully!", "success");
        } else {
            showStatus("Error: " + (result.error || "Failed to save"), "error");
        }
    } catch (err) {
        console.error(err);
        showStatus("Error saving template", "error");
    }
}

// Load template
async function loadTemplate() {
    try {
        const response = await fetch("/templates/load");
        const result = await response.json();

        if (response.ok && result.template) {
            document.getElementById("emailTemplate").value = result.template;
            showStatus("Template loaded successfully!", "success");
        } else {
            showStatus("No saved template found", "error");
        }
    } catch (err) {
        console.error(err);
        showStatus("Error loading template", "error");
    }
}

// Show status message
function showStatus(message, type) {
    const statusElement = document.getElementById("saveStatus");
    statusElement.innerText = message;
    statusElement.className = type; // 'success' or 'error'
    
    // Clear after 3 seconds
    setTimeout(() => {
        statusElement.innerText = "";
        statusElement.className = "";
    }, 3000);
}

// Load template on page load
window.addEventListener("DOMContentLoaded", loadTemplate);