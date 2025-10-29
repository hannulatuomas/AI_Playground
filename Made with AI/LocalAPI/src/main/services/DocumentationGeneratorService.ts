/**
 * DocumentationGeneratorService - Static API Documentation Generator
 * 
 * Generates comprehensive HTML/CSS documentation from OpenAPI specifications
 */

import type { OpenAPISpec } from './OpenAPIGeneratorService';
import * as fs from 'fs';

export interface DocumentationOptions {
  title?: string;
  description?: string;
  version?: string;
  theme?: 'light' | 'dark' | 'modern' | 'classic';
  logo?: string;
  favicon?: string;
  customCss?: string;
  includeExplorer?: boolean;
  includeAuth?: boolean;
  includeExamples?: boolean;
  includeChangelog?: boolean;
  branding?: {
    companyName?: string;
    companyUrl?: string;
    supportEmail?: string;
  };
  changelog?: ChangelogEntry[];
}

export interface ChangelogEntry {
  version: string;
  date: string;
  changes: string[];
  breaking?: boolean;
}

export interface GeneratedDocumentation {
  html: string;
  css: string;
  js?: string;
}

export class DocumentationGeneratorService {
  /**
   * Generate static HTML documentation from OpenAPI spec
   */
  generateDocumentation(
    spec: OpenAPISpec,
    options: DocumentationOptions = {}
  ): GeneratedDocumentation {
    const theme = options.theme || 'modern';
    const html = this.generateHTML(spec, options);
    const css = this.generateCSS(theme, options.customCss);
    const js = options.includeExplorer ? this.generateJS() : undefined;

    return { html, css, js };
  }

  /**
   * Generate HTML content
   */
  private generateHTML(spec: OpenAPISpec, options: DocumentationOptions): string {
    const title = options.title || spec.info.title;
    const version = options.version || spec.info.version;
    const description = options.description || spec.info.description || '';

    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${this.escapeHtml(title)} - API Documentation</title>
  <style>${this.generateCSS(options.theme || 'modern', options.customCss)}</style>
  ${options.includeExplorer ? `<script>${this.generateJS()}</script>` : ''}
</head>
<body>
  ${this.generateHeader(title, version, options)}
  <div class="container">
    ${this.generateSidebar(spec, options)}
    <main class="content">
      ${this.generateOverview(spec, description)}
      ${options.includeAuth !== false && spec.components?.securitySchemes ? 
        this.generateAuthSection(spec.components.securitySchemes) : ''}
      ${this.generateEndpoints(spec, options)}
      ${options.includeChangelog && options.changelog ? 
        this.generateChangelog(options.changelog) : ''}
    </main>
  </div>
  ${this.generateFooter(options)}
</body>
</html>`;
  }

  private generateHeader(title: string, version: string, options: DocumentationOptions): string {
    return `<header class="header">
    <div class="header-content">
      ${options.logo ? `<img src="${options.logo}" alt="Logo" class="logo">` : ''}
      <div class="header-text">
        <h1>${this.escapeHtml(title)}</h1>
        <span class="version">v${this.escapeHtml(version)}</span>
      </div>
    </div>
  </header>`;
  }

  private generateSidebar(spec: OpenAPISpec, options: DocumentationOptions): string {
    const sections: string[] = ['<nav class="sidebar">', '<ul class="nav-list">'];
    sections.push('<li><a href="#overview">Overview</a></li>');
    if (options.includeAuth !== false && spec.components?.securitySchemes) {
      sections.push('<li><a href="#authentication">Authentication</a></li>');
    }
    sections.push('<li class="nav-section">Endpoints</li>');
    for (const path of Object.keys(spec.paths)) {
      sections.push(`<li><a href="#path-${this.slugify(path)}">${this.escapeHtml(path)}</a></li>`);
    }
    sections.push('</ul>', '</nav>');
    return sections.join('\n');
  }

  private generateOverview(spec: OpenAPISpec, description: string): string {
    return `<section id="overview" class="section">
    <h2>Overview</h2>
    ${description ? `<p class="description">${this.escapeHtml(description)}</p>` : ''}
    ${spec.servers && spec.servers.length > 0 ? `
    <div class="servers">
      <h3>Base URLs</h3>
      <ul>${spec.servers.map(s => `<li><code>${this.escapeHtml(s.url)}</code></li>`).join('')}</ul>
    </div>` : ''}
  </section>`;
  }

  private generateAuthSection(securitySchemes: Record<string, any>): string {
    return `<section id="authentication" class="section">
    <h2>Authentication</h2>
    ${Object.entries(securitySchemes).map(([name, scheme]) => `
    <div class="auth-scheme">
      <h3>${this.escapeHtml(name)}</h3>
      <p><strong>Type:</strong> ${this.escapeHtml(scheme.type)}</p>
      ${scheme.scheme ? `<p><strong>Scheme:</strong> ${this.escapeHtml(scheme.scheme)}</p>` : ''}
    </div>`).join('')}
  </section>`;
  }

  private generateEndpoints(spec: OpenAPISpec, options: DocumentationOptions): string {
    const sections: string[] = ['<section class="section"><h2>Endpoints</h2>'];
    for (const [path, pathItem] of Object.entries(spec.paths)) {
      sections.push(this.generatePathItem(path, pathItem, options));
    }
    sections.push('</section>');
    return sections.join('\n');
  }

  private generatePathItem(path: string, pathItem: any, options: DocumentationOptions): string {
    const sections: string[] = [`<div id="path-${this.slugify(path)}" class="path-item">`];
    for (const [method, operation] of Object.entries(pathItem)) {
      if (method === 'parameters') continue;
      sections.push(this.generateOperation(path, method, operation as any, options));
    }
    sections.push('</div>');
    return sections.join('\n');
  }

  private generateOperation(path: string, method: string, operation: any, options: DocumentationOptions): string {
    return `<div class="operation">
    <div class="operation-header">
      <span class="method method-${method}">${method.toUpperCase()}</span>
      <code class="path">${this.escapeHtml(path)}</code>
    </div>
    ${operation.summary ? `<h3>${this.escapeHtml(operation.summary)}</h3>` : ''}
    ${operation.parameters?.length > 0 ? this.generateParameters(operation.parameters) : ''}
    ${operation.requestBody ? this.generateRequestBody(operation.requestBody, options) : ''}
    ${operation.responses ? this.generateResponses(operation.responses, options) : ''}
  </div>`;
  }

  private generateParameters(parameters: any[]): string {
    return `<div class="parameters"><h4>Parameters</h4><table>
      <tr><th>Name</th><th>In</th><th>Type</th><th>Required</th></tr>
      ${parameters.map(p => `<tr>
        <td><code>${this.escapeHtml(p.name)}</code></td>
        <td>${this.escapeHtml(p.in)}</td>
        <td>${this.escapeHtml(p.schema?.type || 'any')}</td>
        <td>${p.required ? 'Yes' : 'No'}</td>
      </tr>`).join('')}
    </table></div>`;
  }

  private generateRequestBody(requestBody: any, options: DocumentationOptions): string {
    const content = requestBody.content || {};
    return `<div class="request-body"><h4>Request Body</h4>
      ${Object.entries(content).map(([ct, mt]: [string, any]) => `
      <div><h5>${this.escapeHtml(ct)}</h5>
      ${options.includeExamples && mt.example ? 
        `<pre><code>${this.escapeHtml(JSON.stringify(mt.example, null, 2))}</code></pre>` : ''}
      </div>`).join('')}
    </div>`;
  }

  private generateResponses(responses: any, options: DocumentationOptions): string {
    return `<div class="responses"><h4>Responses</h4>
      ${Object.entries(responses).map(([status, response]: [string, any]) => `
      <div class="response">
        <h5><span class="status">${status}</span> ${response.description || ''}</h5>
        ${response.content ? Object.entries(response.content).map(([ct, mt]: [string, any]) => `
        <div>${options.includeExamples && mt.example ? 
          `<pre><code>${this.escapeHtml(JSON.stringify(mt.example, null, 2))}</code></pre>` : ''}
        </div>`).join('') : ''}
      </div>`).join('')}
    </div>`;
  }

  private generateChangelog(changelog: ChangelogEntry[]): string {
    return `<section id="changelog" class="section"><h2>Changelog</h2>
      ${changelog.map(entry => `<div class="changelog-entry">
        <h3>${this.escapeHtml(entry.version)} <span>${this.escapeHtml(entry.date)}</span></h3>
        <ul>${entry.changes.map(c => `<li>${this.escapeHtml(c)}</li>`).join('')}</ul>
      </div>`).join('')}
    </section>`;
  }

  private generateFooter(options: DocumentationOptions): string {
    return `<footer class="footer"><p>Generated by LocalAPI</p></footer>`;
  }

  private generateCSS(theme: string, customCss?: string): string {
    const baseCSS = `
/* Reset and Base Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.6;
  color: var(--text-color);
  background-color: var(--bg-color);
}

/* Header */
.header {
  background-color: var(--header-bg);
  color: var(--header-text);
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  max-width: 1400px;
  margin: 0 auto;
}

.logo {
  height: 48px;
  width: auto;
}

.header-text {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header h1 {
  font-size: 2rem;
  font-weight: 600;
  margin: 0;
}

.version {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background-color: var(--accent-color);
  color: white;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
}

/* Container and Layout */
.container {
  display: flex;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 200px);
}

/* Sidebar Navigation */
.sidebar {
  width: 280px;
  background-color: var(--sidebar-bg);
  padding: 2rem 1rem;
  border-right: 1px solid var(--border-color);
  position: sticky;
  top: 100px;
  height: calc(100vh - 100px);
  overflow-y: auto;
}

.nav-list {
  list-style: none;
}

.nav-list li {
  margin-bottom: 0.5rem;
}

.nav-list a {
  color: var(--text-color);
  text-decoration: none;
  display: block;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.nav-list a:hover {
  background-color: var(--hover-bg);
  transform: translateX(4px);
}

.nav-section {
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  color: var(--accent-color);
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Main Content */
.content {
  flex: 1;
  padding: 2rem 3rem;
  max-width: 1000px;
}

/* Sections */
.section {
  margin-bottom: 4rem;
}

.section h2 {
  font-size: 2rem;
  margin-bottom: 1.5rem;
  color: var(--heading-color);
  border-bottom: 3px solid var(--accent-color);
  padding-bottom: 0.75rem;
}

.section h3 {
  font-size: 1.5rem;
  margin: 1.5rem 0 1rem;
  color: var(--heading-color);
}

.description {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
  font-size: 1.05rem;
  line-height: 1.7;
}

/* Servers */
.servers {
  margin: 2rem 0;
  padding: 1.5rem;
  background-color: var(--card-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.servers h3 {
  margin-top: 0;
  font-size: 1.25rem;
}

.servers ul {
  list-style: none;
  padding: 0;
}

.servers li {
  margin: 0.75rem 0;
}

.servers code {
  font-size: 1rem;
}

/* Authentication */
.auth-scheme {
  margin: 1.5rem 0;
  padding: 1.5rem;
  background-color: var(--card-bg);
  border-radius: 8px;
  border-left: 4px solid var(--accent-color);
}

.auth-scheme h3 {
  margin-top: 0;
  color: var(--accent-color);
}

/* Operations */
.operation {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  transition: box-shadow 0.2s ease;
}

.operation:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.operation-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.method {
  display: inline-block;
  padding: 0.4rem 0.9rem;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: white;
  min-width: 80px;
  text-align: center;
}

.method-get { background-color: #61affe; }
.method-post { background-color: #49cc90; }
.method-put { background-color: #fca130; }
.method-patch { background-color: #50e3c2; }
.method-delete { background-color: #f93e3e; }
.method-head { background-color: #9012fe; }
.method-options { background-color: #0d5aa7; }

.path {
  font-family: 'Courier New', Consolas, Monaco, monospace;
  font-size: 1.15rem;
  color: var(--code-color);
  font-weight: 500;
}

.operation h3 {
  font-size: 1.3rem;
  margin: 0 0 1rem 0;
}

/* Parameters */
.parameters,
.request-body,
.responses {
  margin: 1.5rem 0;
}

.parameters h4,
.request-body h4,
.responses h4 {
  font-size: 1.1rem;
  margin-bottom: 1rem;
  color: var(--heading-color);
  font-weight: 600;
}

/* Tables */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  background-color: var(--card-bg);
  border-radius: 6px;
  overflow: hidden;
}

th,
td {
  padding: 0.9rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

th {
  background-color: var(--table-header-bg);
  font-weight: 600;
  color: var(--heading-color);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover {
  background-color: var(--hover-bg);
}

/* Code */
code {
  background-color: var(--code-bg);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-family: 'Courier New', Consolas, Monaco, monospace;
  font-size: 0.9em;
  color: var(--code-color);
}

pre {
  background-color: var(--code-bg);
  padding: 1.25rem;
  border-radius: 6px;
  overflow-x: auto;
  margin: 1rem 0;
  border: 1px solid var(--border-color);
}

pre code {
  background: none;
  padding: 0;
  font-size: 0.9rem;
  line-height: 1.5;
}

/* Status Badges */
.status {
  display: inline-block;
  padding: 0.3rem 0.7rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.85rem;
  color: white;
}

.status-2xx { background-color: #49cc90; }
.status-3xx { background-color: #61affe; }
.status-4xx { background-color: #fca130; }
.status-5xx { background-color: #f93e3e; }

/* Response */
.response {
  margin: 1rem 0;
  padding: 1rem;
  background-color: var(--card-bg);
  border-radius: 6px;
  border-left: 3px solid var(--accent-color);
}

.response h5 {
  margin: 0 0 0.75rem 0;
  font-size: 1.05rem;
}

/* Changelog */
.changelog-entry {
  margin: 2rem 0;
  padding: 1.5rem;
  background-color: var(--card-bg);
  border-radius: 8px;
  border-left: 4px solid var(--accent-color);
}

.changelog-entry h3 {
  margin-top: 0;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.changelog-entry span {
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: normal;
}

.changelog-entry ul {
  margin: 1rem 0 0 1.5rem;
}

.changelog-entry li {
  margin: 0.5rem 0;
}

/* Footer */
.footer {
  background-color: var(--header-bg);
  color: var(--header-text);
  padding: 2rem;
  text-align: center;
  margin-top: 4rem;
}

.footer p {
  margin: 0.5rem 0;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .container {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    position: static;
    height: auto;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
  }
  
  .content {
    padding: 2rem 1.5rem;
  }
}

@media (max-width: 768px) {
  .header h1 {
    font-size: 1.5rem;
  }
  
  .content {
    padding: 1.5rem 1rem;
  }
  
  .operation {
    padding: 1.5rem;
  }
  
  .operation-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  table {
    font-size: 0.85rem;
  }
  
  th, td {
    padding: 0.6rem 0.75rem;
  }
}

/* Try It Out Section */
.try-it-section {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 2px solid var(--border-color);
}

.try-it-button {
  background-color: var(--accent-color);
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.try-it-button:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.try-it-panel {
  margin-top: 1rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.try-it-form,
.try-it-response {
  background-color: var(--card-bg);
  padding: 1.5rem;
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.try-it-form h4,
.try-it-response h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: var(--heading-color);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--heading-color);
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  background-color: var(--code-bg);
  color: var(--text-color);
}

.send-request-button {
  background-color: var(--accent-color);
  color: white;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
  transition: all 0.2s ease;
}

.send-request-button:hover {
  opacity: 0.9;
}

.response-status {
  padding: 0.6rem 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-weight: 600;
}

.response-status.sending {
  background-color: #61affe;
  color: white;
}

.response-status.error {
  background-color: #f93e3e;
  color: white;
}

.response-body {
  max-height: 400px;
  overflow-y: auto;
}

@media (max-width: 1024px) {
  .try-it-panel {
    grid-template-columns: 1fr;
  }
}

/* Scrollbar Styling */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-color);
}

::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--accent-color);
}
`;

    const themes: Record<string, string> = {
      light: `
:root {
  --bg-color: #ffffff;
  --text-color: #333333;
  --text-secondary: #666666;
  --heading-color: #1a1a1a;
  --header-bg: #f8f9fa;
  --header-text: #333333;
  --sidebar-bg: #f8f9fa;
  --card-bg: #ffffff;
  --border-color: #e1e4e8;
  --hover-bg: #e9ecef;
  --accent-color: #0366d6;
  --code-color: #24292e;
  --code-bg: #f6f8fa;
  --table-header-bg: #f6f8fa;
}
`,
      dark: `
:root {
  --bg-color: #0d1117;
  --text-color: #c9d1d9;
  --text-secondary: #8b949e;
  --heading-color: #f0f6fc;
  --header-bg: #161b22;
  --header-text: #f0f6fc;
  --sidebar-bg: #161b22;
  --card-bg: #0d1117;
  --border-color: #30363d;
  --hover-bg: #21262d;
  --accent-color: #58a6ff;
  --code-color: #79c0ff;
  --code-bg: #161b22;
  --table-header-bg: #161b22;
}
`,
      modern: `
:root {
  --bg-color: #fafbfc;
  --text-color: #24292e;
  --text-secondary: #586069;
  --heading-color: #1b1f23;
  --header-bg: #24292e;
  --header-text: #ffffff;
  --sidebar-bg: #ffffff;
  --card-bg: #ffffff;
  --border-color: #e1e4e8;
  --hover-bg: #f6f8fa;
  --accent-color: #2ea44f;
  --code-color: #032f62;
  --code-bg: #f6f8fa;
  --table-header-bg: #fafbfc;
}
`,
      classic: `
:root {
  --bg-color: #f5f5f5;
  --text-color: #212529;
  --text-secondary: #6c757d;
  --heading-color: #343a40;
  --header-bg: #343a40;
  --header-text: #ffffff;
  --sidebar-bg: #ffffff;
  --card-bg: #ffffff;
  --border-color: #dee2e6;
  --hover-bg: #e9ecef;
  --accent-color: #007bff;
  --code-color: #e83e8c;
  --code-bg: #f8f9fa;
  --table-header-bg: #f8f9fa;
}
`
    };
    
    return `${themes[theme] || themes.modern}${baseCSS}${customCss || ''}`;
  }

  private generateJS(): string {
    return `
// Interactive API Explorer
document.addEventListener('DOMContentLoaded', () => {
  // Smooth scrolling for navigation
  document.querySelectorAll('.nav-list a').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // Add "Try It" buttons to each operation
  document.querySelectorAll('.operation').forEach(operation => {
    const header = operation.querySelector('.operation-header');
    if (!header) return;

    const method = header.querySelector('.method')?.textContent?.trim();
    const path = header.querySelector('.path')?.textContent?.trim();
    if (!method || !path) return;

    // Create Try It section
    const trySection = document.createElement('div');
    trySection.className = 'try-it-section';
    trySection.innerHTML = \`
      <button class="try-it-button">Try It Out</button>
      <div class="try-it-panel" style="display: none;">
        <div class="try-it-form">
          <h4>Request</h4>
          <div class="form-group">
            <label>Base URL:</label>
            <input type="text" class="base-url-input" value="http://localhost:3000" />
          </div>
          <div class="form-group">
            <label>Headers (JSON):</label>
            <textarea class="headers-input" rows="3">{"Content-Type": "application/json"}</textarea>
          </div>
          <div class="form-group body-group" style="display: none;">
            <label>Body (JSON):</label>
            <textarea class="body-input" rows="5">{}</textarea>
          </div>
          <button class="send-request-button">Send Request</button>
        </div>
        <div class="try-it-response">
          <h4>Response</h4>
          <div class="response-status"></div>
          <pre class="response-body"></pre>
        </div>
      </div>
    \`;

    operation.appendChild(trySection);

    // Show/hide body input for methods that support it
    if (['POST', 'PUT', 'PATCH'].includes(method)) {
      trySection.querySelector('.body-group').style.display = 'block';
    }

    // Toggle panel
    const button = trySection.querySelector('.try-it-button');
    const panel = trySection.querySelector('.try-it-panel');
    button.addEventListener('click', () => {
      const isHidden = panel.style.display === 'none';
      panel.style.display = isHidden ? 'block' : 'none';
      button.textContent = isHidden ? 'Hide' : 'Try It Out';
    });

    // Send request
    const sendButton = trySection.querySelector('.send-request-button');
    sendButton.addEventListener('click', async () => {
      const baseUrl = trySection.querySelector('.base-url-input').value;
      const headersText = trySection.querySelector('.headers-input').value;
      const bodyText = trySection.querySelector('.body-input').value;
      const statusDiv = trySection.querySelector('.response-status');
      const responseBody = trySection.querySelector('.response-body');

      try {
        statusDiv.textContent = 'Sending...';
        statusDiv.className = 'response-status sending';
        responseBody.textContent = '';

        let headers = {};
        try {
          headers = JSON.parse(headersText);
        } catch (e) {
          throw new Error('Invalid headers JSON');
        }

        const fetchOptions = {
          method: method,
          headers: headers,
        };

        if (['POST', 'PUT', 'PATCH'].includes(method)) {
          fetchOptions.body = bodyText;
        }

        const url = baseUrl + path;
        const response = await fetch(url, fetchOptions);
        
        statusDiv.textContent = \`Status: \${response.status} \${response.statusText}\`;
        statusDiv.className = \`response-status status-\${Math.floor(response.status / 100)}xx\`;

        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json();
          responseBody.textContent = JSON.stringify(data, null, 2);
        } else {
          const text = await response.text();
          responseBody.textContent = text;
        }
      } catch (error) {
        statusDiv.textContent = 'Error: ' + error.message;
        statusDiv.className = 'response-status error';
        responseBody.textContent = error.stack || error.message;
      }
    });
  });
});`;
  }

  private escapeHtml(text: string): string {
    const map: Record<string, string> = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
  }

  private slugify(text: string): string {
    return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  }

  /**
   * Save documentation to directory
   */
  saveToDirectory(doc: GeneratedDocumentation, outputDir: string): void {
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    fs.writeFileSync(`${outputDir}/index.html`, doc.html);
    if (doc.js) {
      fs.writeFileSync(`${outputDir}/explorer.js`, doc.js);
    }
  }
}
