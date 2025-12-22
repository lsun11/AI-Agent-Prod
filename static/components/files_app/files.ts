// static/components/files_app/files.ts

export type FileSystemItem = {
    name: string;
    type: "folder" | "file";
    ext?: "pdf" | "docx" | "txt" | "pptx";
    date?: string;
    children?: FileSystemItem[];
};

export class FilesGadget {
    private root: HTMLElement;
    private gridEl: HTMLElement | null;
    private pathEl: HTMLElement | null;
    private navItems: NodeListOf<HTMLElement>;
    private refreshBtn: HTMLButtonElement | null;

    // State
    private fileSystem: FileSystemItem[] = [];
    private currentPath: string[] = ["root"];
    private currentFolder: FileSystemItem[] = [];

    constructor(root: HTMLElement) {
        this.root = root;
        this.gridEl = root.querySelector("#files-grid");
        this.pathEl = root.querySelector("#files-current-path");
        this.navItems = root.querySelectorAll(".files-nav-item");
        this.refreshBtn = root.querySelector("#files-refresh-btn");

        this.initListeners();
        void this.refresh();
    }

    private initListeners() {
        this.navItems.forEach(item => {
            item.addEventListener("click", () => {
                const pathKey = item.getAttribute("data-path");

                this.navItems.forEach(n => n.classList.remove("active"));
                item.classList.add("active");

                if (pathKey === "root") {
                    this.navigate(["root"], this.fileSystem);
                } else if (pathKey === "ai_agent") {
                    const folder = this.fileSystem.find(f => f.name === "AI Agent")?.children || [];
                    this.navigate(["root", "AI Agent"], folder);
                } else if (pathKey === "weather") {
                    const folder = this.fileSystem.find(f => f.name === "Weather App")?.children || [];
                    this.navigate(["root", "Weather App"], folder);
                }
            });
        });

        if (this.refreshBtn) {
            this.refreshBtn.addEventListener("click", () => void this.refresh());
        }
    }

    private async deleteFile(filename: string) {
        if (!confirm(`Are you sure you want to delete "${filename}"?`)) return;

        try {
            const resp = await fetch(`/files/delete/${encodeURIComponent(filename)}`, {
                method: "DELETE"
            });

            if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.detail || "Delete failed");
            }

            await this.refresh();

        } catch (e: any) {
            alert(`Error: ${e.message}`);
        }
    }

    /**
     * Helper: Walk the new file tree to find the folder matching a path array.
     */
    private findFolderByPath(pathNames: string[], rootSystem: FileSystemItem[]): FileSystemItem[] | null {
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
            } else {
                return null; // Path no longer exists
            }
        }
        return currentLevel;
    }

    public async refresh() {
        // 1. Remember where we were before loading
        const savedPath = [...this.currentPath];

        if (this.gridEl) {
            // Optional: show a small loading spinner or opacity change instead of clearing everything
            this.gridEl.style.opacity = "0.5";
        }

        try {
            const resp = await fetch("/files/structure");
            if (!resp.ok) throw new Error("Failed to load files");

            this.fileSystem = await resp.json();

            // 2. Try to restore the view to the saved path
            const targetFolder = this.findFolderByPath(savedPath, this.fileSystem);

            if (targetFolder) {
                // Success: Stay in current folder
                this.currentFolder = targetFolder;
                this.render(); // Re-render with new data
            } else {
                // Fallback: If current folder was deleted or lost, go to Root
                console.warn("Could not restore path, resetting to root.");
                this.navigate(["root"], this.fileSystem);
            }

        } catch (e) {
            console.error(e);
            if (this.gridEl) {
                this.gridEl.innerHTML = `<div style="grid-column:1/-1; text-align:center; color:red;">Error loading files</div>`;
            }
        } finally {
            if (this.gridEl) this.gridEl.style.opacity = "1";
        }
    }

    private navigate(pathDisplay: string[], content: FileSystemItem[]) {
        this.currentPath = pathDisplay;
        this.currentFolder = content;
        this.render();
    }

    private getIcon(item: FileSystemItem): string {
        if (item.type === "folder") return "📁";
        if (item.ext === "pdf") return "📄";
        if (item.ext === "docx") return "📝";
        if (item.ext === "pptx") return "📊";
        if (item.ext === "txt") return "📃";
        return "📄";
    }

    public render() {
        if (!this.gridEl || !this.pathEl) return;

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
                if ((e.target as HTMLElement).closest(".file-delete-btn")) {
                    e.stopPropagation();
                    this.deleteFile(item.name);
                    return;
                }

                if (item.type === "folder" && item.children) {
                    this.navigate([...this.currentPath, item.name], item.children);
                } else {
                    const url = `/download/${encodeURIComponent(item.name)}`;
                    window.open(url, "_blank");
                }
            });

            this.gridEl!.appendChild(el);
        });
    }
}