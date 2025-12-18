// static/chat-helpers.ts
import { markdownToHtml } from "./markdown.js";
import { RECOMMENDATION_STARTERS } from "./types.js";
import { makePanelDraggable } from "./drag.js";
/**
 * Extracts a website URL from a chunk of markdown/text.
 */
export function extractWebsiteUrl(text) {
    const lines = text.split("\n");
    for (const line of lines) {
        const m1 = line.match(/Website[:：]\s*(https?:\/\/\S+)/i);
        const m2 = line.match(/网站[:：]\s*(https?:\/\/\S+)/i);
        const m = m1 || m2;
        if (m) {
            // @ts-ignore
            return m[1].trim().replace(/[)\]]+$/, "");
        }
    }
    return undefined;
}
/**
 * Splits the LLM reply into logical “bubbles”.
 * (Same logic you had in ChatUI before, just extracted.)
 */
export function splitReplyIntoBubbles(reply) {
    const lines = reply.split(/\r?\n/);
    const bubbles = [];
    let current = [];
    const flush = () => {
        const text = current.join("\n").trim();
        if (text) {
            bubbles.push(text);
        }
        current = [];
    };
    for (const rawLine of lines) {
        const line = rawLine;
        const trimmed = rawLine.trim();
        if (!trimmed && current.length === 0)
            continue;
        if (trimmed.startsWith("📊 Results for:")) {
            flush();
            current.push(line);
            continue;
        }
        if (/^\d+\.\s*🏢/.test(trimmed)) {
            flush();
            current.push(line);
            continue;
        }
        if (RECOMMENDATION_STARTERS.some(starter => trimmed.startsWith(starter))) {
            flush();
            current.push(line);
            continue;
        }
        current.push(line);
    }
    flush();
    return bubbles;
}
/**
 * Builds a company bubble DOM node with a tiled, semi-transparent logo background.
 */
export function createCompanyBubbleElement(text, company) {
    const wrapper = document.createElement("div");
    wrapper.className = "message bot company-bubble";
    // We’re layering background + foreground; keep bubble styling but add positioning
    wrapper.style.position = "relative";
    wrapper.style.overflow = "hidden";
    // Logo background overlay (tiled, semi-transparent)
    if (company.logo_url) {
        const bg = document.createElement("div");
        bg.className = "company-logo-bg";
        bg.style.position = "absolute";
        bg.style.inset = "0";
        bg.style.zIndex = "0";
        bg.style.pointerEvents = "none";
        bg.style.backgroundImage = `url(${company.logo_url})`;
        bg.style.backgroundRepeat = "repeat";
        bg.style.backgroundPosition = "center";
        bg.style.backgroundSize = "240px 240px"; // tweak if you like
        bg.style.opacity = "0.08"; // subtle
        wrapper.appendChild(bg);
    }
    // Foreground content
    const inner = document.createElement("div");
    inner.className = "company-bubble-inner";
    inner.style.position = "relative";
    inner.style.zIndex = "1";
    const bodyEl = document.createElement("div");
    bodyEl.className = "company-body";
    bodyEl.innerHTML = markdownToHtml(text);
    inner.appendChild(bodyEl);
    wrapper.appendChild(inner);
    // Make bubble clickable to open website if available
    if (company.website) {
        wrapper.classList.add("clickable");
        wrapper.addEventListener("click", () => {
            window.open(company.website, "_blank");
        });
    }
    return wrapper;
}
function buildFormatUrl(baseUrl, format) {
    // Adjust this if your backend uses a different format pattern.
    try {
        const url = new URL(baseUrl, window.location.origin);
        url.searchParams.set("format", format);
        return url.toString();
    }
    catch (_a) {
        const sep = baseUrl.includes("?") ? "&" : "?";
        return `${baseUrl}${sep}format=${format}`;
    }
}
function getPreviewPanelElements() {
    const panel = document.getElementById("file-preview-panel");
    const titleEl = document.getElementById("file-preview-title");
    const bodyEl = document.getElementById("file-preview-body");
    const formatSelect = document.getElementById("file-preview-format");
    const downloadBtn = document.getElementById("file-preview-download");
    const closeBtn = document.getElementById("file-preview-close");
    if (panel && titleEl) {
        makePanelDraggable(panel, titleEl, {
            mode: "boundary",
        });
    }
    return { panel, titleEl, bodyEl, formatSelect, downloadBtn, closeBtn };
}
/**
 * Open / update the side preview panel for pdf/txt/pptx.
 */
export function openFilePreview(config) {
    const { panel, titleEl, bodyEl, formatSelect, downloadBtn, closeBtn } = getPreviewPanelElements();
    if (!panel || !titleEl || !bodyEl || !formatSelect || !downloadBtn || !closeBtn) {
        console.warn("file preview panel elements not found in DOM");
        return;
    }
    // Decide available formats
    const availableFormats = [];
    if (config.urls.pdf)
        availableFormats.push("pdf");
    if (config.urls.txt)
        availableFormats.push("txt");
    if (config.urls.pptx)
        availableFormats.push("pptx");
    if (availableFormats.length === 0) {
        console.warn("No previewable formats found", config.urls);
        return;
    }
    // Pick initial format: preferred → pdf → txt → pptx
    const preferred = config.preferred;
    let currentFormat = (preferred && availableFormats.includes(preferred)) ? preferred :
        (availableFormats.includes("pdf") ? "pdf" :
            availableFormats.includes("txt") ? "txt" : "pptx");
    // Populate title
    titleEl.textContent = config.title;
    // Populate format selector
    formatSelect.innerHTML = "";
    for (const fmt of availableFormats) {
        const opt = document.createElement("option");
        opt.value = fmt;
        opt.textContent =
            fmt === "pdf" ? "PDF" :
                fmt === "txt" ? "Text" :
                    "Slides (PPTX)";
        if (fmt === currentFormat)
            opt.selected = true;
        formatSelect.appendChild(opt);
    }
    function renderBody(format) {
        const url = format === "pdf" ? config.urls.pdf :
            format === "txt" ? config.urls.txt :
                config.urls.pptx;
        if (!url)
            return;
        bodyEl.innerHTML = "";
        if (format === "txt") {
            fetch(url)
                .then((res) => res.text())
                .then((text) => {
                const pre = document.createElement("pre");
                pre.textContent = text;
                bodyEl.appendChild(pre);
            })
                .catch((err) => {
                console.error("Failed to load txt preview:", err);
                const pre = document.createElement("pre");
                pre.textContent = "Failed to load text preview.";
                bodyEl.appendChild(pre);
            });
        }
        else if (format === "pdf") {
            const embed = document.createElement("embed");
            embed.src = url + "#view=FitH";
            embed.type = "application/pdf";
            embed.style.width = "100%";
            embed.style.height = "100%";
            bodyEl.appendChild(embed);
        }
        else {
            // PPTX: browser will usually download; show helper message + link
            const msg = document.createElement("div");
            msg.style.padding = "12px";
            msg.style.fontSize = "13px";
            msg.textContent =
                "Slides preview is limited in this view. Click “Open” to view or download the PPTX file.";
            const btn = document.createElement("button");
            btn.type = "button";
            btn.style.marginTop = "8px";
            btn.textContent = "Open PPTX";
            btn.onclick = () => window.open(url, "_blank");
            msg.appendChild(document.createElement("br"));
            msg.appendChild(btn);
            bodyEl.appendChild(msg);
        }
    }
    // initial render
    renderBody(currentFormat);
    // wire format selector
    formatSelect.onchange = () => {
        const val = formatSelect.value;
        if (availableFormats.includes(val)) {
            currentFormat = val;
            renderBody(currentFormat);
        }
    };
    // download button
    downloadBtn.onclick = () => {
        const url = currentFormat === "pdf" ? config.urls.pdf :
            currentFormat === "txt" ? config.urls.txt :
                config.urls.pptx;
        if (url) {
            window.open(url, "_blank");
        }
    };
    function hidePanel() {
        bodyEl.innerHTML = "";
        panel.classList.remove("visible");
        panel.style.display = "none";
    }
    // close button
    closeBtn.onclick = (ev) => {
        ev.stopPropagation();
        hidePanel();
    };
    // finally show the panel
    panel.style.display = "flex";
    panel.classList.add("visible");
}
/**
 * Creates the “Download summary” button container.
 *
 * If multiFormat = false:
 *   - Single button which opens the given URL.
 *
 * If multiFormat = true:
 *   - Main button + hover menu with [PDF, DOCX, TXT].
 *   - Clicking a format opens baseUrl with ?format=<fmt>.
 */
export function createDownloadButtonElement(urlsOrUrl, object, language, enableMultiFormatMenu = false) {
    const downloadContainer = document.createElement("div");
    downloadContainer.className = "download-container";
    const mainButton = document.createElement("button");
    mainButton.type = "button";
    mainButton.className = "download-button";
    mainButton.textContent =
        language === "Eng"
            ? `Download summary (${object})`
            : `下载总结 (${object})`;
    let urls = null;
    // Legacy: simple string url
    if (typeof urlsOrUrl === "string") {
        const url = urlsOrUrl;
        mainButton.addEventListener("click", () => {
            window.open(url, "_blank");
        });
        downloadContainer.appendChild(mainButton);
        return downloadContainer;
    }
    // Multi-format map: { pdf, docx, txt, pptx? }
    urls = urlsOrUrl;
    // Default click: if multi-format menu is enabled, open best format (pdf > txt > docx > pptx)
    mainButton.addEventListener("click", () => {
        var _a, _b, _c;
        const url = (_c = (_b = (_a = urls === null || urls === void 0 ? void 0 : urls.pdf) !== null && _a !== void 0 ? _a : urls === null || urls === void 0 ? void 0 : urls.txt) !== null && _b !== void 0 ? _b : urls === null || urls === void 0 ? void 0 : urls.docx) !== null && _c !== void 0 ? _c : urls === null || urls === void 0 ? void 0 : urls.pptx;
        if (url) {
            window.open(url, "_blank");
        }
    });
    downloadContainer.appendChild(mainButton);
    // Optional hover menu for per-format downloads (what you had before)
    if (enableMultiFormatMenu && urls) {
        const menu = document.createElement("div");
        menu.className = "download-menu";
        menu.style.display = "none";
        function addFormatButton(label, fmtKey) {
            const url = urls && urls[fmtKey];
            if (!url)
                return;
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "download-option";
            btn.textContent = label;
            btn.addEventListener("click", (ev) => {
                ev.stopPropagation();
                window.open(url, "_blank");
            });
            menu.appendChild(btn);
        }
        // e.g. "PDF", "DOCX", "TXT"
        if (language === "Eng") {
            addFormatButton("PDF", "pdf");
            addFormatButton("DOCX", "docx");
            addFormatButton("Text (TXT)", "txt");
        }
        else {
            addFormatButton("PDF 文件", "pdf");
            addFormatButton("Word 文档 (DOCX)", "docx");
            addFormatButton("纯文本 (TXT)", "txt");
        }
        downloadContainer.appendChild(menu);
        downloadContainer.addEventListener("mouseenter", () => {
            if (menu.childElementCount > 0) {
                menu.style.display = "flex";
            }
        });
        downloadContainer.addEventListener("mouseleave", () => {
            menu.style.display = "none";
        });
    }
    // === Preview button: open in-app panel (pdf/txt/pptx) ===
    if (urls) {
        const previewBtn = document.createElement("button");
        previewBtn.type = "button";
        previewBtn.className = "preview-button";
        previewBtn.textContent = language === "Eng" ? "Preview" : "预览";
        previewBtn.addEventListener("click", (ev) => {
            ev.stopPropagation();
            openFilePreview({
                title: language === "Eng"
                    ? `Preview: ${object}`
                    : `预览：${object}`,
                urls,
                preferred: "pdf",
            });
        });
        downloadContainer.appendChild(previewBtn);
    }
    return downloadContainer;
}
//# sourceMappingURL=chat-helpers.js.map