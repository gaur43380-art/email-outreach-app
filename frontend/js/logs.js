// logs.js

// Load logs from backend
function loadLogs() {
  document.getElementById('logStatus').innerText = 'Loading...';
  
  fetch("/logs/my")
    .then(res => {
      if (!res.ok) {
        throw new Error('Failed to fetch logs');
      }
      return res.json();
    })
    .then(logs => {
      const tbody = document.querySelector("#logTable tbody");
      tbody.innerHTML = ""; // Clear previous rows

      if (logs.length === 0) {
        // No logs yet
        const row = tbody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 4;
        cell.style.textAlign = "center";
        cell.style.color = "#666";
        cell.innerText = "No email logs found. Start sending emails to see logs here.";
        document.getElementById('logStatus').innerText = '';
        return;
      }

      // Add each log as a row
      logs.forEach(log => {
        const row = tbody.insertRow();
        
        // Email
        row.insertCell().innerText = log.email;
        
        // Status (with color coding)
        const statusCell = row.insertCell();
        statusCell.innerText = log.status;
        
        // Apply status-specific styling
        if (log.status.includes('SENT') || log.status.includes('FOLLOWUP')) {
          statusCell.className = 'status-sent';
        } else if (log.status === 'REPLIED') {
          statusCell.className = 'status-replied';
        } else if (log.status === 'BOUNCED') {
          statusCell.className = 'status-bounced';
        } else if (log.status === 'FAILED') {
          statusCell.className = 'status-failed';
        }
        
        // Time (formatted)
        const timeCell = row.insertCell();
        try {
          timeCell.innerText = new Date(log.time).toLocaleString();
        } catch (e) {
          timeCell.innerText = log.time || '-';
        }
        
        // Error (with styling if present)
        const errorCell = row.insertCell();
        if (log.error) {
          errorCell.innerHTML = `<span class="error-text">${log.error}</span>`;
        } else {
          errorCell.innerText = "-";
        }
      });

      document.getElementById('logStatus').innerText = `Showing ${logs.length} log(s)`;
    })
    .catch(err => {
      console.error("Failed to fetch logs:", err);
      
      const tbody = document.querySelector("#logTable tbody");
      tbody.innerHTML = "";
      const row = tbody.insertRow();
      const cell = row.insertCell();
      cell.colSpan = 4;
      cell.style.textAlign = "center";
      cell.style.color = "red";
      cell.innerText = "Error loading logs. Please try again.";
      
      document.getElementById('logStatus').innerText = 'Error loading logs';
    });
}

// Load logs when page loads
window.addEventListener('DOMContentLoaded', loadLogs);

// Auto-refresh every 30 seconds
setInterval(loadLogs, 30000);

