# Frontend Integration Example

This document provides examples of how to integrate the new S3-based AI-to-CAD workflow in the frontend.

## 🔄 Complete Workflow Implementation

### 1. AI Chat with S3 Integration

```javascript
// Enhanced chat component with S3 integration
class AIChat {
  constructor(projectId) {
    this.projectId = projectId;
    this.currentStatus = 'idle';
    this.statusInterval = null;
  }

  async sendMessage(message) {
    try {
      // Update UI to show generating status
      this.updateStatus('generating', 'Generating script…');
      
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify({
          message: message,
          project_id: this.projectId,
          context: {
            engine: 'cadquery',
            parameters: this.getProjectParameters()
          }
        })
      });

      const result = await response.json();
      
      if (result.message.role === 'assistant') {
        // Display AI response
        this.displayMessage(result.message);
        
        // Check if S3 upload was successful
        if (result.message.content.includes('Code saved to S3')) {
          this.updateStatus('uploading', 'Uploading to S3…');
          
          // Start polling for processing status
          this.startStatusPolling();
        }
      }
      
    } catch (error) {
      console.error('Chat error:', error);
      this.updateStatus('error', 'Failed to generate code');
    }
  }

  startStatusPolling() {
    // Poll every 10 seconds for status updates
    this.statusInterval = setInterval(async () => {
      await this.checkProcessingStatus();
    }, 10000);
  }

  async checkProcessingStatus() {
    try {
      const response = await fetch(`/api/projects/${this.projectId}/status`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });
      
      const status = await response.json();
      
      if (status.success) {
        const statusInfo = status.status_info;
        
        switch (statusInfo.status) {
          case 'processing':
            this.updateStatus('processing', 'FreeCAD processing…');
            break;
            
          case 'completed':
            this.updateStatus('completed', 'Model ready — view or download');
            this.showDownloadOptions(statusInfo.available_formats);
            this.stopStatusPolling();
            break;
            
          case 'timeout':
            this.updateStatus('timeout', 'Processing timeout - please try again');
            this.stopStatusPolling();
            break;
        }
      }
      
    } catch (error) {
      console.error('Status check error:', error);
    }
  }

  stopStatusPolling() {
    if (this.statusInterval) {
      clearInterval(this.statusInterval);
      this.statusInterval = null;
    }
  }

  updateStatus(status, message) {
    this.currentStatus = status;
    
    // Update status indicator in UI
    const statusElement = document.getElementById('processing-status');
    if (statusElement) {
      statusElement.textContent = message;
      statusElement.className = `status-indicator status-${status}`;
    }
  }

  showDownloadOptions(formats) {
    const downloadContainer = document.getElementById('download-options');
    if (!downloadContainer) return;
    
    downloadContainer.innerHTML = '';
    
    formats.forEach(format => {
      const button = document.createElement('button');
      button.textContent = `Download ${format}`;
      button.className = 'download-btn';
      button.onclick = () => this.downloadFile(format);
      downloadContainer.appendChild(button);
    });
    
    downloadContainer.style.display = 'block';
  }

  async downloadFile(format) {
    try {
      const response = await fetch(`/api/projects/${this.projectId}/download/${format}`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });
      
      const result = await response.json();
      
      if (result.success && result.download_url) {
        // Open download URL in new tab
        window.open(result.download_url, '_blank');
      } else {
        throw new Error('Failed to generate download URL');
      }
      
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download file');
    }
  }

  getAuthToken() {
    return localStorage.getItem('authToken');
  }

  getProjectParameters() {
    // Get current project parameters from UI
    return {
      width: document.getElementById('width')?.value || 10,
      height: document.getElementById('height')?.value || 10,
      depth: document.getElementById('depth')?.value || 10
    };
  }
}
```

### 2. Script Version Management

```javascript
// Script version management component
class ScriptVersionManager {
  constructor(projectId) {
    this.projectId = projectId;
  }

  async loadVersions() {
    try {
      const response = await fetch(`/api/projects/${this.projectId}/scripts`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        this.displayVersions(result.scripts);
      }
      
    } catch (error) {
      console.error('Failed to load versions:', error);
    }
  }

  displayVersions(scripts) {
    const versionList = document.getElementById('version-list');
    if (!versionList) return;
    
    versionList.innerHTML = '';
    
    scripts.forEach(script => {
      const versionItem = document.createElement('div');
      versionItem.className = 'version-item';
      versionItem.innerHTML = `
        <div class="version-header">
          <span class="version-number">v${script.version}</span>
          <span class="version-date">${new Date(script.last_modified).toLocaleDateString()}</span>
        </div>
        <div class="version-actions">
          <button onclick="this.viewScript(${script.version})">View Code</button>
          <button onclick="this.downloadScript(${script.version})">Download</button>
        </div>
      `;
      versionList.appendChild(versionItem);
    });
  }

  async viewScript(version) {
    try {
      const response = await fetch(`/api/projects/${this.projectId}/script/${version}`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        this.showCodeModal(result.content, version);
      }
      
    } catch (error) {
      console.error('Failed to load script:', error);
    }
  }

  showCodeModal(code, version) {
    // Create and show modal with code content
    const modal = document.createElement('div');
    modal.className = 'code-modal';
    modal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h3>Script Version ${version}</h3>
          <button class="close-btn" onclick="this.remove()">&times;</button>
        </div>
        <div class="modal-body">
          <pre><code class="language-python">${this.escapeHtml(code)}</code></pre>
        </div>
        <div class="modal-footer">
          <button onclick="this.copyToClipboard('${this.escapeForJs(code)}')">Copy Code</button>
          <button onclick="this.remove()">Close</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Syntax highlighting if available
    if (window.Prism) {
      Prism.highlightAll();
    }
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  escapeForJs(text) {
    return text.replace(/'/g, "\\'").replace(/\n/g, '\\n');
  }

  copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
      alert('Code copied to clipboard!');
    });
  }

  getAuthToken() {
    return localStorage.getItem('authToken');
  }
}
```

### 3. Project Status Dashboard

```javascript
// Project status dashboard component
class ProjectStatusDashboard {
  constructor(projectId) {
    this.projectId = projectId;
    this.refreshInterval = null;
  }

  async initialize() {
    await this.loadProjectStatus();
    this.startAutoRefresh();
  }

  async loadProjectStatus() {
    try {
      const response = await fetch(`/api/monitoring/projects/${this.projectId}/processing-status`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        this.updateDashboard(result);
      }
      
    } catch (error) {
      console.error('Failed to load project status:', error);
    }
  }

  updateDashboard(statusData) {
    // Update overall status
    const statusElement = document.getElementById('overall-status');
    if (statusElement) {
      statusElement.textContent = statusData.status_message;
      statusElement.className = `status-badge status-${statusData.overall_status}`;
    }

    // Update script info
    this.updateScriptInfo(statusData.details.scripts);
    
    // Update output files info
    this.updateOutputInfo(statusData.details.output_files);
    
    // Update logs info
    this.updateLogsInfo(statusData.details.logs);
  }

  updateScriptInfo(scriptData) {
    const scriptInfo = document.getElementById('script-info');
    if (!scriptInfo) return;
    
    scriptInfo.innerHTML = `
      <h4>Scripts</h4>
      <p>Total versions: ${scriptData.count}</p>
      ${scriptData.latest_version ? `<p>Latest: v${scriptData.latest_version}</p>` : ''}
      <div class="versions">
        ${scriptData.versions.map(v => `<span class="version-tag">v${v}</span>`).join('')}
      </div>
    `;
  }

  updateOutputInfo(outputData) {
    const outputInfo = document.getElementById('output-info');
    if (!outputInfo) return;
    
    if (outputData.count > 0) {
      outputInfo.innerHTML = `
        <h4>Output Files</h4>
        <p>Available: ${outputData.count} files</p>
        <p>Formats: ${outputData.formats.join(', ')}</p>
        <div class="download-buttons">
          ${outputData.formats.map(format => 
            `<button onclick="this.downloadFormat('${format}')">${format}</button>`
          ).join('')}
        </div>
      `;
    } else {
      outputInfo.innerHTML = `
        <h4>Output Files</h4>
        <p>No output files available yet</p>
      `;
    }
  }

  updateLogsInfo(logData) {
    const logInfo = document.getElementById('log-info');
    if (!logInfo) return;
    
    if (logData.count > 0) {
      logInfo.innerHTML = `
        <h4>Processing Logs</h4>
        <p>Available: ${logData.count} log files</p>
        ${logData.latest ? `
          <p>Latest: ${logData.latest.filename}</p>
          <button onclick="this.viewLogs()">View Logs</button>
        ` : ''}
      `;
    } else {
      logInfo.innerHTML = `
        <h4>Processing Logs</h4>
        <p>No logs available</p>
      `;
    }
  }

  async downloadFormat(format) {
    try {
      const response = await fetch(`/api/projects/${this.projectId}/download/${format}`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        window.open(result.download_url, '_blank');
      }
      
    } catch (error) {
      console.error('Download failed:', error);
    }
  }

  async viewLogs() {
    try {
      const response = await fetch(`/api/projects/${this.projectId}/logs`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });
      
      const result = await response.json();
      
      if (result.success && result.log_files.length > 0) {
        const latestLog = result.log_files[0];
        await this.showLogContent(latestLog.filename);
      }
      
    } catch (error) {
      console.error('Failed to load logs:', error);
    }
  }

  async showLogContent(filename) {
    try {
      const response = await fetch(`/api/projects/${this.projectId}/logs/${filename}`, {
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        this.showLogModal(result.content, filename);
      }
      
    } catch (error) {
      console.error('Failed to load log content:', error);
    }
  }

  showLogModal(content, filename) {
    const modal = document.createElement('div');
    modal.className = 'log-modal';
    modal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h3>Processing Log: ${filename}</h3>
          <button class="close-btn" onclick="this.remove()">&times;</button>
        </div>
        <div class="modal-body">
          <pre class="log-content">${this.escapeHtml(content)}</pre>
        </div>
        <div class="modal-footer">
          <button onclick="this.remove()">Close</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
  }

  startAutoRefresh() {
    // Refresh every 30 seconds
    this.refreshInterval = setInterval(() => {
      this.loadProjectStatus();
    }, 30000);
  }

  stopAutoRefresh() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
    }
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  getAuthToken() {
    return localStorage.getItem('authToken');
  }
}
```

### 4. CSS Styles for Status Indicators

```css
/* Status indicators */
.status-indicator {
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 500;
  display: inline-block;
}

.status-generating {
  background-color: #e3f2fd;
  color: #1976d2;
}

.status-uploading {
  background-color: #f3e5f5;
  color: #7b1fa2;
}

.status-processing {
  background-color: #fff3e0;
  color: #f57c00;
  animation: pulse 2s infinite;
}

.status-completed {
  background-color: #e8f5e8;
  color: #2e7d32;
}

.status-error, .status-timeout {
  background-color: #ffebee;
  color: #c62828;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

/* Download options */
.download-options {
  margin-top: 16px;
  display: none;
}

.download-btn {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 8px 16px;
  margin: 4px;
  border-radius: 4px;
  cursor: pointer;
}

.download-btn:hover {
  background-color: #45a049;
}

/* Version management */
.version-item {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 12px;
  margin: 8px 0;
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.version-number {
  font-weight: bold;
  color: #1976d2;
}

.version-actions button {
  margin-right: 8px;
  padding: 4px 8px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  border-radius: 3px;
}

/* Modals */
.code-modal, .log-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 80%;
  max-height: 80%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 16px;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-body {
  padding: 16px;
  overflow: auto;
  flex: 1;
}

.modal-footer {
  padding: 16px;
  border-top: 1px solid #ddd;
  text-align: right;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
}

/* Log content */
.log-content {
  background-color: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
  max-height: 400px;
  overflow-y: auto;
}
```

### 5. Usage Example

```javascript
// Initialize components when page loads
document.addEventListener('DOMContentLoaded', function() {
  const projectId = getCurrentProjectId(); // Your function to get current project ID
  
  // Initialize AI chat
  const aiChat = new AIChat(projectId);
  
  // Initialize version manager
  const versionManager = new ScriptVersionManager(projectId);
  versionManager.loadVersions();
  
  // Initialize status dashboard
  const statusDashboard = new ProjectStatusDashboard(projectId);
  statusDashboard.initialize();
  
  // Set up chat form
  const chatForm = document.getElementById('chat-form');
  if (chatForm) {
    chatForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const messageInput = document.getElementById('message-input');
      if (messageInput.value.trim()) {
        aiChat.sendMessage(messageInput.value.trim());
        messageInput.value = '';
      }
    });
  }
});
```

This example shows how to integrate all the new S3-based features into your frontend, providing a complete user experience from AI code generation to file download.
