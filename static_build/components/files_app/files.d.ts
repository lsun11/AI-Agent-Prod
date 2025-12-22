export type FileSystemItem = {
    name: string;
    type: "folder" | "file";
    ext?: "pdf" | "docx" | "txt" | "pptx";
    date?: string;
    children?: FileSystemItem[];
};
export declare class FilesGadget {
    private root;
    private gridEl;
    private pathEl;
    private navItems;
    private refreshBtn;
    private fileSystem;
    private currentPath;
    private currentFolder;
    constructor(root: HTMLElement);
    private initListeners;
    private deleteFile;
    /**
     * Helper: Walk the new file tree to find the folder matching a path array.
     */
    private findFolderByPath;
    refresh(): Promise<void>;
    private navigate;
    private getIcon;
    render(): void;
}
//# sourceMappingURL=files.d.ts.map