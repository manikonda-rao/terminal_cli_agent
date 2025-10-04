/**
 * Interactive Code Execution Panel JavaScript
 * Handles real-time code execution, WebSocket communication, and UI interactions.
 */

class ExecutionPanel {
    constructor() {
        this.socket = null;
        this.sessionId = null;
        this.codeEditor = null;
        this.isExecuting = false;
        this.currentTheme = 'light';
        this.history = [];
        
        this.init();
    }
    
    init() {
        this.setupSocketConnection();
        this.setupCodeEditor();
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
        this.loadTheme();
        this.updateUI();
    }
    
    setupSocketConnection() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.updateStatus('Connected', 'success');
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.updateStatus('Disconnected', 'error');
        });
        
        this.socket.on('connected', (data) => {
            this.sessionId = data.session_id;
            document.getElementById('session-id').textContent = `Session: ${this.sessionId.substring(0, 8)}...`;
        });
        
        this.socket.on('execution_started', (data) => {
            this.isExecuting = true;
            this.updateStatus('Executing...', 'running');
            this.showLoadingOverlay();
            this.updateButtons();
        });
        
        this.socket.on('execution_output', (data) => {
            this.addOutputLine(data.message, data.type);
        });
        
        this.socket.on('execution_complete', (data) => {
            this.isExecuting = false;
            this.hideLoadingOverlay();
            this.updateStatus('Execution Complete', 'success');
            this.updateButtons();
            
            // Add to history
            this.addToHistory(data);
            
            // Display result
            if (data.status === 'completed') {
                this.addOutputLine('✅ Execution completed successfully', 'success');
                if (data.stdout) {
                    this.addOutputLine('Output:', 'info');
                    data.stdout.split('\n').forEach(line => {
                        if (line.trim()) {
                            this.addOutputLine(line, '');
                        }
                    });
                }
            } else {
                this.addOutputLine(`❌ Execution failed: ${data.status}`, 'error');
                if (data.stderr) {
                    this.addOutputLine('Error output:', 'error');
                    data.stderr.split('\n').forEach(line => {
                        if (line.trim()) {
                            this.addOutputLine(line, 'error');
                        }
                    });
                }
            }
            
            this.addOutputLine(`Execution time: ${data.execution_time.toFixed(3)}s`, 'info');
            this.addOutputLine('─'.repeat(50), '');
        });
        
        this.socket.on('execution_error', (data) => {
            this.isExecuting = false;
            this.hideLoadingOverlay();
            this.updateStatus('Execution Error', 'error');
            this.updateButtons();
            this.addOutputLine(`❌ Execution error: ${data.error}`, 'error');
        });
        
        this.socket.on('execution_stopped', (data) => {
            this.isExecuting = false;
            this.hideLoadingOverlay();
            this.updateStatus('Execution Stopped', 'warning');
            this.updateButtons();
            this.addOutputLine('🛑 Execution stopped by user', 'warning');
        });
    }
    
    setupCodeEditor() {
        const textarea = document.getElementById('code-editor');
        
        this.codeEditor = CodeMirror.fromTextArea(textarea, {
            mode: 'python',
            theme: 'default',
            lineNumbers: true,
            indentUnit: 4,
            indentWithTabs: false,
            lineWrapping: true,
            autoCloseBrackets: true,
            matchBrackets: true,
            foldGutter: true,
            gutters: ['CodeMirror-linenumbers', 'CodeMirror-foldgutter'],
            extraKeys: {
                'Ctrl-Enter': () => this.runCode(),
                'Ctrl-L': () => this.clearOutput(),
                'Ctrl-Shift-T': () => this.toggleTheme()
            }
        });
        
        // Set default code
        this.codeEditor.setValue(`# Enter your code here...
# Press Ctrl+Enter to run
# Press Ctrl+L to clear output

print('Hello, World!')`);
        
        // Update editor mode when language changes
        document.getElementById('language-selector').addEventListener('change', (e) => {
            this.updateEditorMode(e.target.value);
        });
    }
    
    setupEventListeners() {
        // Run button
        document.getElementById('run-button').addEventListener('click', () => {
            this.runCode();
        });
        
        // Stop button
        document.getElementById('stop-button').addEventListener('click', () => {
            this.stopExecution();
        });
        
        // Clear button
        document.getElementById('clear-button').addEventListener('click', () => {
            this.clearOutput();
        });
        
        // Theme toggle
        document.getElementById('theme-toggle').addEventListener('click', () => {
            this.toggleTheme();
        });
        
        // Panel controls
        document.getElementById('toggle-panel').addEventListener('click', () => {
            this.togglePanelSize();
        });
        
        document.getElementById('copy-output').addEventListener('click', () => {
            this.copyOutput();
        });
        
        // History controls
        document.getElementById('clear-history').addEventListener('click', () => {
            this.clearHistory();
        });
        
        document.getElementById('toggle-history').addEventListener('click', () => {
            this.toggleHistoryPanel();
        });
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Prevent default for our shortcuts
            if (e.ctrlKey) {
                switch (e.key) {
                    case 'Enter':
                        e.preventDefault();
                        this.runCode();
                        break;
                    case 'l':
                        e.preventDefault();
                        this.clearOutput();
                        break;
                    case 'c':
                        if (this.isExecuting) {
                            e.preventDefault();
                            this.stopExecution();
                        }
                        break;
                }
            }
            
            if (e.ctrlKey && e.shiftKey) {
                switch (e.key) {
                    case 'T':
                        e.preventDefault();
                        this.toggleTheme();
                        break;
                    case 'E':
                        e.preventDefault();
                        this.togglePanelSize();
                        break;
                }
            }
        });
    }
    
    updateEditorMode(language) {
        const modes = {
            'python': 'python',
            'javascript': 'javascript',
            'typescript': 'javascript',
            'java': 'clike',
            'cpp': 'clike',
            'rust': 'rust',
            'go': 'go',
            'php': 'php',
            'ruby': 'ruby',
            'perl': 'perl',
            'bash': 'shell'
        };
        
        const mode = modes[language] || 'python';
        this.codeEditor.setOption('mode', mode);
        
        // Update placeholder text
        const placeholder = this.getPlaceholderText(language);
        this.codeEditor.setValue(placeholder);
    }
    
    getPlaceholderText(language) {
        const placeholders = {
            'python': `# Python code
print('Hello, World!')`,
            'javascript': `// JavaScript code
console.log('Hello, World!');`,
            'typescript': `// TypeScript code
console.log('Hello, World!');`,
            'java': `// Java code
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}`,
            'cpp': `// C++ code
#include <iostream>
int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}`,
            'rust': `// Rust code
fn main() {
    println!("Hello, World!");
}`,
            'go': `// Go code
package main
import "fmt"
func main() {
    fmt.Println("Hello, World!")
}`,
            'php': `<?php
// PHP code
echo "Hello, World!";
?>`,
            'ruby': `# Ruby code
puts "Hello, World!"`,
            'perl': `# Perl code
print "Hello, World!\n";`,
            'bash': `#!/bin/bash
# Bash script
echo "Hello, World!"`
        };
        
        return placeholders[language] || placeholders['python'];
    }
    
    runCode() {
        if (this.isExecuting) {
            this.showToast('Execution already in progress', 'warning');
            return;
        }
        
        const code = this.codeEditor.getValue().trim();
        if (!code) {
            this.showToast('No code to execute', 'warning');
            return;
        }
        
        const language = document.getElementById('language-selector').value;
        
        this.socket.emit('execute_code', {
            code: code,
            language: language,
            session_id: this.sessionId,
            timeout: 30
        });
    }
    
    stopExecution() {
        if (!this.isExecuting) {
            this.showToast('No execution in progress', 'warning');
            return;
        }
        
        this.socket.emit('stop_execution', {
            session_id: this.sessionId
        });
    }
    
    clearOutput() {
        const outputContent = document.getElementById('output-content');
        outputContent.innerHTML = '<div class="output-placeholder">Output will appear here when you run code...</div>';
    }
    
    addOutputLine(text, type = '') {
        const outputContent = document.getElementById('output-content');
        
        // Remove placeholder if it exists
        const placeholder = outputContent.querySelector('.output-placeholder');
        if (placeholder) {
            placeholder.remove();
        }
        
        const line = document.createElement('div');
        line.className = `output-line ${type}`;
        line.textContent = text;
        
        outputContent.appendChild(line);
        outputContent.scrollTop = outputContent.scrollHeight;
    }
    
    addToHistory(data) {
        const historyItem = {
            id: Date.now(),
            code: data.code || this.codeEditor.getValue(),
            language: document.getElementById('language-selector').value,
            status: data.status,
            execution_time: data.execution_time,
            timestamp: new Date().toLocaleTimeString(),
            stdout: data.stdout,
            stderr: data.stderr
        };
        
        this.history.unshift(historyItem);
        
        // Keep only last 50 items
        if (this.history.length > 50) {
            this.history = this.history.slice(0, 50);
        }
        
        this.updateHistoryDisplay();
    }
    
    updateHistoryDisplay() {
        const historyContent = document.getElementById('history-content');
        
        if (this.history.length === 0) {
            historyContent.innerHTML = '<div class="history-placeholder">No execution history yet...</div>';
            return;
        }
        
        historyContent.innerHTML = this.history.map(item => `
            <div class="history-item" onclick="executionPanel.loadFromHistory('${item.id}')">
                <div class="history-item-header">
                    <span class="history-item-language">${item.language}</span>
                    <span class="history-item-time">${item.timestamp}</span>
                </div>
                <div class="history-item-status ${item.status === 'completed' ? 'success' : 'error'}">
                    ${item.status}
                </div>
                <div class="history-item-code">${item.code.substring(0, 100)}${item.code.length > 100 ? '...' : ''}</div>
            </div>
        `).join('');
    }
    
    loadFromHistory(itemId) {
        const item = this.history.find(h => h.id == itemId);
        if (item) {
            this.codeEditor.setValue(item.code);
            document.getElementById('language-selector').value = item.language;
            this.updateEditorMode(item.language);
            this.showToast('Code loaded from history', 'info');
        }
    }
    
    clearHistory() {
        this.history = [];
        this.updateHistoryDisplay();
        this.showToast('History cleared', 'info');
    }
    
    toggleHistoryPanel() {
        const panel = document.getElementById('history-panel');
        panel.classList.toggle('collapsed');
    }
    
    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        
        // Update CodeMirror theme
        const theme = this.currentTheme === 'dark' ? 'monokai' : 'default';
        this.codeEditor.setOption('theme', theme);
        
        // Update theme toggle button
        const themeButton = document.getElementById('theme-toggle');
        themeButton.textContent = this.currentTheme === 'dark' ? '☀️' : '🌙';
        
        // Save theme preference
        localStorage.setItem('execution-panel-theme', this.currentTheme);
        
        this.showToast(`Theme switched to ${this.currentTheme}`, 'info');
    }
    
    loadTheme() {
        const savedTheme = localStorage.getItem('execution-panel-theme') || 'light';
        this.currentTheme = savedTheme;
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        
        const theme = this.currentTheme === 'dark' ? 'monokai' : 'default';
        this.codeEditor.setOption('theme', theme);
        
        const themeButton = document.getElementById('theme-toggle');
        themeButton.textContent = this.currentTheme === 'dark' ? '☀️' : '🌙';
    }
    
    togglePanelSize() {
        const codePanel = document.querySelector('.code-panel');
        const outputPanel = document.querySelector('.output-panel');
        
        if (codePanel.style.flex === '2') {
            codePanel.style.flex = '1';
            outputPanel.style.flex = '1';
        } else {
            codePanel.style.flex = '2';
            outputPanel.style.flex = '1';
        }
        
        this.showToast('Panel size toggled', 'info');
    }
    
    copyOutput() {
        const outputContent = document.getElementById('output-content');
        const text = outputContent.textContent;
        
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Output copied to clipboard', 'success');
        }).catch(() => {
            this.showToast('Failed to copy output', 'error');
        });
    }
    
    updateStatus(text, type) {
        const statusIndicator = document.getElementById('status-indicator');
        const statusText = statusIndicator.querySelector('.status-text');
        
        statusText.textContent = text;
        statusIndicator.className = `status-indicator ${type}`;
    }
    
    updateButtons() {
        const runButton = document.getElementById('run-button');
        const stopButton = document.getElementById('stop-button');
        
        runButton.disabled = this.isExecuting;
        stopButton.disabled = !this.isExecuting;
    }
    
    showLoadingOverlay() {
        document.getElementById('loading-overlay').classList.remove('hidden');
    }
    
    hideLoadingOverlay() {
        document.getElementById('loading-overlay').classList.add('hidden');
    }
    
    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        container.appendChild(toast);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
    
    updateUI() {
        this.updateButtons();
        this.updateHistoryDisplay();
    }
}

// Initialize the execution panel when the page loads
let executionPanel;
document.addEventListener('DOMContentLoaded', () => {
    executionPanel = new ExecutionPanel();
});
