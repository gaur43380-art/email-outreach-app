// dashboard.js

// Load user info and settings on page load
async function loadUserInfo() {
    try {
        const response = await fetch('/me');
        const user = await response.json();

        if (user.authenticated) {
            // Update user info
            document.getElementById('userName').innerText = user.full_name || 'Not set';
            document.getElementById('userEmail').innerText = user.email;
            
            // Gmail status
            document.getElementById('gmailStatus').innerHTML = user.gmail_connected 
                ? '✅ Connected' 
                : '❌ Not Connected';
            
            // Sheet status
            document.getElementById('sheetStatus').innerHTML = user.sheet_id 
                ? '✅ Connected' 
                : '❌ Not Connected';
            
            // Resume status
            document.getElementById('resumeStatus').innerHTML = user.resume_link 
                ? '✅ Added' 
                : '❌ Not Added';
            
            // Sending status
            document.getElementById('sendingStatus').innerHTML = user.is_paused 
                ? '⏸️ Paused' 
                : '▶️ Active';
        }

        // ✅ NEW: Load settings separately to check templates
        await loadTemplateStatus();
    } catch (err) {
        console.error('Error loading user info:', err);
    }
}

// ✅ NEW: Check template status separately
async function loadTemplateStatus() {
    try {
        const response = await fetch('/user/settings');
        const data = await response.json();

        if (!data.error) {
            // Check if templates are set
            const hasInitial = data.email_template && data.email_template.trim();
            const hasFollowup = data.followup_template && data.followup_template.trim();
            const hasSubject = data.email_subject && data.email_subject.trim();
            
            if (hasInitial && hasFollowup && hasSubject) {
                document.getElementById('templateStatus').innerHTML = '✅ All Set';
            } else if (hasInitial || hasFollowup) {
                document.getElementById('templateStatus').innerHTML = '⚠️ Partially Set';
            } else {
                document.getElementById('templateStatus').innerHTML = '❌ Not Set';
            }
        }
    } catch (err) {
        console.error('Error loading template status:', err);
    }
}

// Load settings
async function loadSettings() {
    try {
        const response = await fetch('/user/settings');
        const data = await response.json();

        if (!data.error) {
            document.getElementById('full_name').value = data.full_name || '';
            document.getElementById('resume_link').value = data.resume_link || '';
            document.getElementById('sheet_id').value = data.sheet_id || '';
            document.getElementById('email_subject').value = data.email_subject || '';
            document.getElementById('email_template').value = data.email_template || '';
            document.getElementById('followup_template').value = data.followup_template || '';
        }
    } catch (err) {
        console.error('Error loading settings:', err);
    }
}

// Save settings
async function saveSettings() {
    const settings = {
        full_name: document.getElementById('full_name').value,
        resume_link: document.getElementById('resume_link').value,
        sheet_id: document.getElementById('sheet_id').value,
        email_subject: document.getElementById('email_subject').value,
        email_template: document.getElementById('email_template').value,
        followup_template: document.getElementById('followup_template').value
    };

    // Validation
    if (!settings.full_name || !settings.full_name.trim()) {
        alert('❌ Please enter your full name');
        return;
    }

    if (!settings.email_template || !settings.email_template.trim()) {
        alert('❌ Please set your initial email template');
        return;
    }

    if (!settings.followup_template || !settings.followup_template.trim()) {
        alert('❌ Please set your follow-up email template');
        return;
    }

    if (!settings.email_subject || !settings.email_subject.trim()) {
        alert('❌ Please set your email subject line');
        return;
    }

    try {
        const response = await fetch('/user/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });

        const result = await response.json();
        const statusElement = document.getElementById('settingsStatus');

        if (result.status === 'success') {
            statusElement.innerHTML = '<span style="color: green;">✅ Settings saved!</span>';
            // Reload user info to update status
            await loadUserInfo();
            await loadTemplateStatus();
        } else {
            statusElement.innerHTML = '<span style="color: red;">❌ Error: ' + (result.error || 'Failed to save') + '</span>';
        }

        // Clear status after 3 seconds
        setTimeout(() => {
            statusElement.innerHTML = '';
        }, 3000);
    } catch (err) {
        console.error('Error saving settings:', err);
        document.getElementById('settingsStatus').innerHTML = '<span style="color: red;">❌ Error saving settings</span>';
    }
}

// Connect Gmail
function connectGmail() {
    window.location.href = '/auth/gmail/connect';
}

// Start sending
async function startSending() {
    try {
        const response = await fetch('/user/start', { method: 'POST' });
        const result = await response.json();

        if (response.ok) {
            alert('✅ ' + result.message);
            document.getElementById('status').innerText = result.message;
        } else {
            alert('❌ Error: ' + (result.error || 'Failed to start'));
            document.getElementById('status').innerText = 'Error: ' + (result.error || 'Failed to start');
        }
    } catch (err) {
        console.error(err);
        alert('❌ Error starting sending process');
    }
}

// Pause sending
async function pauseSending() {
    try {
        const response = await fetch('/user/pause', { method: 'POST' });
        if (response.ok) {
            document.getElementById('status').innerText = '⏸️ Sending paused';
            loadUserInfo(); // Refresh status
        }
    } catch (err) {
        console.error(err);
    }
}

// Resume sending
async function resumeSending() {
    try {
        const response = await fetch('/user/resume', { method: 'POST' });
        if (response.ok) {
            document.getElementById('status').innerText = '▶️ Sending resumed';
            loadUserInfo(); // Refresh status
        }
    } catch (err) {
        console.error(err);
    }
}

// Load everything when page loads
window.addEventListener('DOMContentLoaded', () => {
    loadUserInfo();
    loadSettings();
});