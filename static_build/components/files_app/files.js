// static/components/files_app/files.ts
export class FilesGadget {
    constructor(root) {
        // State
        this.fileSystem = [];
        this.currentPath = ["root"];
        this.currentFolder = [];
        this.root = root;
        this.gridEl = root.querySelector("#files-grid");
        this.pathEl = root.querySelector("#files-current-path");
        this.navItems = root.querySelectorAll(".files-nav-item");
        this.refreshBtn = root.querySelector("#files-refresh-btn");
        this.initListeners();
        void this.refresh();
    }
    initListeners() {
        this.navItems.forEach(item => {
            item.addEventListener("click", () => {
                var _a, _b;
                const pathKey = item.getAttribute("data-path");
                this.navItems.forEach(n => n.classList.remove("active"));
                item.classList.add("active");
                if (pathKey === "root") {
                    this.navigate(["root"], this.fileSystem);
                }
                else if (pathKey === "ai_agent") {
                    const folder = ((_a = this.fileSystem.find(f => f.name === "AI Agent")) === null || _a === void 0 ? void 0 : _a.children) || [];
                    this.navigate(["root", "AI Agent"], folder);
                }
                else if (pathKey === "weather") {
                    const folder = ((_b = this.fileSystem.find(f => f.name === "Weather App")) === null || _b === void 0 ? void 0 : _b.children) || [];
                    this.navigate(["root", "Weather App"], folder);
                }
            });
        });
        if (this.refreshBtn) {
            this.refreshBtn.addEventListener("click", () => void this.refresh());
        }
    }
    async deleteFile(filename) {
        if (!confirm(`Are you sure you want to delete "${filename}"?`))
            return;
        try {
            const resp = await fetch(`/files/delete/${encodeURIComponent(filename)}`, {
                method: "DELETE"
            });
            if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.detail || "Delete failed");
            }
            await this.refresh();
        }
        catch (e) {
            alert(`Error: ${e.message}`);
        }
    }
    /**
     * Helper: Walk the new file tree to find the folder matching a path array.
     */
    findFolderByPath(pathNames, rootSystem) {
        // If path is just ["root"], return the top-level array
        if (pathNames.length === 1 && pathNames[0] === "root") {
            return rootSystem;
        }
        // Otherwise, traverse down
        let currentLevel = rootSystem;
        // Skip the first "root" element in pathNames
        for (let i = 1; i < pathNames.length; i++) {
            const folderName = pathNames[i];
            const found = currentLevel.find(item => item.name === folderName && item.type === "folder");
            if (found && found.children) {
                currentLevel = found.children;
            }
            else {
                return null; // Path no longer exists
            }
        }
        return currentLevel;
    }
    async refresh() {
        // 1. Remember where we were before loading
        const savedPath = [...this.currentPath];
        if (this.gridEl) {
            // Optional: show a small loading spinner or opacity change instead of clearing everything
            this.gridEl.style.opacity = "0.5";
        }
        try {
            const resp = await fetch("/files/structure");
            if (!resp.ok)
                throw new Error("Failed to load files");
            this.fileSystem = await resp.json();
            // 2. Try to restore the view to the saved path
            const targetFolder = this.findFolderByPath(savedPath, this.fileSystem);
            if (targetFolder) {
                // Success: Stay in current folder
                this.currentFolder = targetFolder;
                this.render(); // Re-render with new data
            }
            else {
                // Fallback: If current folder was deleted or lost, go to Root
                console.warn("Could not restore path, resetting to root.");
                this.navigate(["root"], this.fileSystem);
            }
        }
        catch (e) {
            console.error(e);
            if (this.gridEl) {
                this.gridEl.innerHTML = `<div style="grid-column:1/-1; text-align:center; color:red;">Error loading files</div>`;
            }
        }
        finally {
            if (this.gridEl)
                this.gridEl.style.opacity = "1";
        }
    }
    navigate(pathDisplay, content) {
        this.currentPath = pathDisplay;
        this.currentFolder = content;
        this.render();
    }
    getIcon(item) {
        if (item.type === "folder")
            return "📁";
        if (item.ext === "pdf")
            return "📄";
        if (item.ext === "docx")
            return "📝";
        if (item.ext === "pptx")
            return "📊";
        if (item.ext === "txt")
            return "📃";
        return "📄";
    }
    render() {
        if (!this.gridEl || !this.pathEl)
            return;
        this.pathEl.textContent = this.currentPath.join(" > ");
        this.gridEl.innerHTML = "";
        if (!this.currentFolder || this.currentFolder.length === 0) {
            this.gridEl.innerHTML = `<div style="grid-column:1/-1; text-align:center; color:#999; margin-top:40px;">This folder is empty</div>`;
            return;
        }
        this.currentFolder.forEach(item => {
            const el = document.createElement("div");
            el.className = "file-item";
            const deleteHtml = item.type === "file"
                ? `<button class="file-delete-btn" title="Delete">🗑️</button>`
                : "";
            el.innerHTML = `
                ${deleteHtml}
                <div class="file-icon">${this.getIcon(item)}</div>
                <div class="file-name">${item.name}</div>
                ${item.date ? `<div class="file-date">${item.date}</div>` : ""}
            `;
            el.addEventListener("click", (e) => {
                if (e.target.closest(".file-delete-btn")) {
                    e.stopPropagation();
                    this.deleteFile(item.name);
                    return;
                }
                if (item.type === "folder" && item.children) {
                    this.navigate([...this.currentPath, item.name], item.children);
                }
                else {
                    const url = `/download/${encodeURIComponent(item.name)}`;
                    window.open(url, "_blank");
                }
            });
            this.gridEl.appendChild(el);
        });
    }
}
//# sourceMappingURL=files.js.map