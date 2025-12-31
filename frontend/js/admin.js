// admin.js

// Load all users
function loadUsers() {
  fetch("/admin/users")
    .then(res => {
      if (!res.ok) {
        throw new Error('Failed to fetch users');
      }
      return res.json();
    })
    .then(users => {
      const tbody = document.querySelector("#usersTable tbody");
      tbody.innerHTML = ""; // Clear existing rows

      if (users.length === 0) {
        const row = tbody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 6;
        cell.className = "empty-cell";
        cell.innerText = "No users found";
        return;
      }

      // Calculate stats
      const activeCount = users.filter(u => !u.is_paused).length;
      const pausedCount = users.filter(u => u.is_paused).length;
      
      document.getElementById('totalUsers').innerText = users.length;
      document.getElementById('activeUsers').innerText = activeCount;
      document.getElementById('pausedUsers').innerText = pausedCount;

      // Add each user as a row
      users.forEach(u => {
        const row = tbody.insertRow();
        
        // Email
        row.insertCell().innerText = u.email;
        
        // Gmail status
        const gmailCell = row.insertCell();
        gmailCell.innerHTML = u.gmail_connected 
          ? '<span class="badge badge-success">✓ Connected</span>' 
          : '<span class="badge badge-danger">✗ Not Connected</span>';
        
        // Sheet status
        const sheetCell = row.insertCell();
        sheetCell.innerHTML = u.sheet_id 
          ? '<span class="badge badge-success">✓ Connected</span>' 
          : '<span class="badge badge-danger">✗ Not Connected</span>';
        
        // Resume status
        const resumeCell = row.insertCell();
        resumeCell.innerHTML = u.resume_link 
          ? '<span class="badge badge-success">✓ Added</span>' 
          : '<span class="badge badge-warning">✗ Not Added</span>';
        
        // Sending status
        const statusCell = row.insertCell();
        statusCell.innerHTML = u.is_paused 
          ? '<span class="badge badge-warning">⏸️ Paused</span>' 
          : '<span class="badge badge-success">▶️ Active</span>';

        // Action button
        const actionCell = row.insertCell();
        const btn = document.createElement("button");
        btn.className = u.is_paused ? "btn-success" : "btn-warning";
        btn.innerText = u.is_paused ? "Resume" : "Pause";
        btn.onclick = () => toggleUserStatus(u.id, u.is_paused);
        actionCell.appendChild(btn);
      });
    })
    .catch(err => {
      console.error("Failed to fetch users:", err);
      const tbody = document.querySelector("#usersTable tbody");
      tbody.innerHTML = '<tr><td colspan="6" class="error-cell">Error loading users. Please refresh.</td></tr>';
    });
}

// Toggle user status (pause/resume)
function toggleUserStatus(userId, isPaused) {
  const action = isPaused ? "resume" : "pause";
  const confirmMsg = isPaused 
    ? "Resume email sending for this user?" 
    : "Pause email sending for this user?";
  
  if (!confirm(confirmMsg)) {
    return;
  }

  fetch(`/admin/${action}/${userId}`, {
    method: "POST"
  })
  .then(res => {
    if (!res.ok) {
      throw new Error('Action failed');
    }
    return res.json();
  })
  .then(() => {
    loadUsers(); // Reload the table
  })
  .catch(err => {
    console.error("Action failed:", err);
    alert("Failed to " + action + " user. Please try again.");
  });
}

// Load users on page load
window.addEventListener('DOMContentLoaded', loadUsers);

// Auto-refresh every 30 seconds
setInterval(loadUsers, 30000);