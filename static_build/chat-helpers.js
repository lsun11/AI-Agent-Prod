// static/chat-helpers.ts
import { markdownToHtml } from "./markdown.js";
import { RECOMMENDATION_STARTERS } from "./types.js";
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
// Implementation
export function createDownloadButtonElement(urlOrUrls, object, language, multiFormat = false) {
    const downloadContainer = document.createElement("div");
    downloadContainer.className = "download-container";
    const button = document.createElement("button");
    button.type = "button";
    button.className = "download-button";
    button.textContent =
        language === "Eng"
            ? `Download summary (${object})`
            : `下载总结 (${object})`;
    downloadContainer.appendChild(button);
    const isMultiUrls = typeof urlOrUrls === "object" && urlOrUrls !== null;
    // --- Simple single-file behaviour (slides, or non-multi usage) ---
    if (!multiFormat || !isMultiUrls) {
        const singleUrl = typeof urlOrUrls === "string" ? urlOrUrls : urlOrUrls.pdf;
        button.addEventListener("click", () => {
            window.open(singleUrl, "_blank");
        });
        return downloadContainer;
    }
    // --- Fancy multi-format hover menu (PDF / DOCX / TXT) ---
    const urls = urlOrUrls;
    const menu = document.createElement("div");
    menu.className = "download-format-menu hidden";
    const formats = [
        {
            key: "pdf",
            label: language === "Eng" ? "PDF" : "PDF 文档",
        },
        {
            key: "docx",
            label: language === "Eng" ? "DOCX" : "Word 文档",
        },
        {
            key: "txt",
            label: language === "Eng" ? "TXT" : "纯文本",
        },
    ];
    formats.forEach(({ key, label }) => {
        const fmtBtn = document.createElement("button");
        fmtBtn.type = "button";
        fmtBtn.className = "download-format-btn";
        fmtBtn.textContent = label;
        fmtBtn.addEventListener("click", (ev) => {
            ev.stopPropagation();
            const targetUrl = urls[key];
            if (targetUrl) {
                window.open(targetUrl, "_blank");
            }
        });
        menu.appendChild(fmtBtn);
    });
    downloadContainer.appendChild(menu);
    // Optional: main button click defaults to PDF
    button.addEventListener("click", () => {
        if (urls.pdf) {
            window.open(urls.pdf, "_blank");
        }
    });
    // Show / hide on hover
    let hideTimeout = null;
    const showMenu = () => {
        if (hideTimeout !== null) {
            window.clearTimeout(hideTimeout);
            hideTimeout = null;
        }
        menu.classList.remove("hidden");
    };
    const hideMenu = () => {
        hideTimeout = window.setTimeout(() => {
            menu.classList.add("hidden");
        }, 120);
    };
    downloadContainer.addEventListener("mouseenter", showMenu);
    downloadContainer.addEventListener("mouseleave", hideMenu);
    return downloadContainer;
}
//# sourceMappingURL=chat-helpers.js.map