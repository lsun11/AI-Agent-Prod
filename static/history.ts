// static/history.ts
import {makePanelDraggable} from "./drag.js";
import type {LanguageCode} from "./types.js";

type HistoryEntry = {
    id: string;
    query: string;
    topic?: string | null;
    language?: string;
    created_at?: string;
    download_pdf_url?: string | null;
    download_docx_url?: string | null;
    download_txt_url?: string | null;
    slides_download_url?: string | null;
};

function formatDateForHistory(iso?: string | null): string {
    if (!iso) return "";
    try {
        const d = new Date(iso);
        return d.toLocaleString();
    } catch {
        return iso ?? "";
    }
}

function openDownload(url: string) {
    window.open(url, "_blank");
}

async function fetchHistory(limit = 20): Promise<HistoryEntry[]> {
    const res = await fetch(`/history?limit=${limit}`);
    if (!res.ok) return [];
    const data = await res.json();
    if (!Array.isArray(data)) return [];
    return data;
}

function renderHistoryItem(entry: HistoryEntry): HTMLDivElement {
    const wrapper = document.createElement("div");
    wrapper.className = "history-item";

    const q = document.createElement("div");
    q.className = "history-query";
    q.textContent = entry.query || "(no query)";
    wrapper.appendChild(q);

    const meta = document.createElement("div");
    meta.className = "history-meta";
    const topic = entry.topic || "";
    const ts = formatDateForHistory(entry.created_at);
    meta.textContent = [topic, ts].filter(Boolean).join(" · ");
    wrapper.appendChild(meta);

    const links = document.createElement("div");
    links.className = "history-links";

    if (entry.download_pdf_url) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "history-link";
        btn.textContent = "PDF";
        btn.addEventListener("click", (ev) => {
            ev.stopPropagation();
            openDownload(entry.download_pdf_url!);
        });
        links.appendChild(btn);
    }

    if (entry.download_docx_url) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "history-link";
        btn.textContent = "DOCX";
        btn.addEventListener("click", (ev) => {
            ev.stopPropagation();
            openDownload(entry.download_docx_url!);
        });
        links.appendChild(btn);
    }

    if (entry.download_txt_url) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "history-link";
        btn.textContent = "TXT";
        btn.addEventListener("click", (ev) => {
            ev.stopPropagation();
            openDownload(entry.download_txt_url!);
        });
        links.appendChild(btn);
    }

    if (entry.slides_download_url) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "history-link";
        btn.textContent = "Slides";
        btn.addEventListener("click", (ev) => {
            ev.stopPropagation();
            openDownload(entry.slides_download_url!);
        });
        links.appendChild(btn);
    }

    if (links.childElementCount > 0) {
        wrapper.appendChild(links);
    }

    // Optional: clicking the whole item re-fills the input with the old query
    wrapper.addEventListener("click", () => {
        const input = document.getElementById("user-input") as
            | HTMLTextAreaElement
            | HTMLInputElement
            | null;
        if (input && entry.query) {
            input.value = entry.query;
            input.focus();
        }
    });

    return wrapper;
}

export async function initHistoryPanel(): Promise<void> {
    let panel = document.getElementById("history-panel") as HTMLDivElement | null;
    const list = document.getElementById("history-list") as HTMLDivElement | null;

    if (!panel) {
        panel = document.createElement("div");
        panel.id = "history-panel";
        panel.className = "history-panel";
        document.body.appendChild(panel);
    }

    // Header (drag handle)
    let header = panel.querySelector(".history-header") as HTMLElement | null;
    if (!header) {
        header = document.createElement("div");
        header.className = "history-header";
        panel.prepend(header);
    }

    // 🔽 Add expand/collapse toggle button
    setupHistoryToggle(panel, header, list);

    // Make the panel draggable by its header
    makePanelDraggable(panel, header);

    try {
        const items = await fetchHistory(30);

        if (list) {
            list.innerHTML = "";

            if (items.length === 0) {
                const empty = document.createElement("div");
                empty.className = "history-empty";
                empty.textContent = "No past reports yet.";
                list.appendChild(empty);
                return;
            }

            for (const item of items) {
                list.appendChild(renderHistoryItem(item));
            }
        }
    } catch (err) {
        console.error("Failed to load history:", err);
        if (list) {
            list.innerHTML = "";
            const errorEl = document.createElement("div");
            errorEl.className = "history-empty";
            errorEl.textContent = "Failed to load history.";
            list.appendChild(errorEl);
        }
    }
}

/**
 * Add a small expand/collapse toggle in the header.
 * - Click on header (not button) → drag panel
 * - Click on button → collapse/expand list
 */
function setupHistoryToggle(
  panel: HTMLElement,
  header: HTMLElement,
  listEl: HTMLElement | null,
): void {
  // ensure there is always a label span
  let labelSpan = header.querySelector(".history-header-label") as HTMLSpanElement | null;
  if (!labelSpan) {
    labelSpan = document.createElement("span");
    labelSpan.className = "history-header-label";
    labelSpan.textContent = "History";
    header.prepend(labelSpan);
  }

    // ---------- Clear button ----------
  let clearBtn = header.querySelector(".history-clear") as HTMLButtonElement | null;
  if (!clearBtn) {
    clearBtn = document.createElement("button");
    clearBtn.type = "button";
    clearBtn.className = "history-clear";
    clearBtn.title = "Clear history";

    // label will be updated by language sync
    clearBtn.textContent = "Clear";

    clearBtn.addEventListener("pointerdown", (e) => e.stopPropagation());
    clearBtn.addEventListener("click", async (e) => {
      e.stopPropagation();

      const ok = window.confirm(
        panel.dataset.lang === "Chn"
          ? "确定要清空历史记录吗？"
          : "Clear all history?"
      );
      if (!ok) return;

      try {
        const res = await fetch("/history/clear", { method: "POST" });
        if (!res.ok) throw new Error("Failed");
        if (listEl) listEl.innerHTML = "";
      } catch (err) {
        alert("Failed to clear history");
      }
    });

    header.appendChild(clearBtn);
  }

  let toggleBtn = header.querySelector(".history-toggle") as HTMLButtonElement | null;
  if (!toggleBtn) {
    toggleBtn = document.createElement("button");
    toggleBtn.type = "button";
    toggleBtn.className = "history-toggle";
    toggleBtn.title = "Collapse / expand history";
    toggleBtn.textContent = "▲";

    // Prevent drag start when interacting with the button
    toggleBtn.addEventListener("pointerdown", (event) => {
      event.stopPropagation();
    });

    toggleBtn.addEventListener("click", (event) => {
      event.stopPropagation();
      const collapsed = panel.classList.toggle("history-panel--collapsed");
      if (listEl) {
        listEl.style.display = collapsed ? "none" : "";
      }
      toggleBtn!.textContent = collapsed ? "▼" : "▲";
      toggleBtn!.setAttribute("aria-expanded", collapsed ? "false" : "true");
    });

    header.appendChild(toggleBtn);
  }

  // Ensure initial visual state matches DOM (collapsed by default now)
  const collapsed = panel.classList.contains("history-panel--collapsed");
  if (listEl) {
    listEl.style.display = collapsed ? "none" : "";
  }
  toggleBtn.textContent = collapsed ? "▼" : "▲";
  toggleBtn.setAttribute("aria-expanded", collapsed ? "false" : "true");
}


export function setHistoryHeaderLanguage(language: LanguageCode): void {
  const header = document.querySelector(".history-header") as HTMLElement | null;
  if (!header) return;

  let labelSpan = header.querySelector(".history-header-label") as HTMLSpanElement | null;
  if (!labelSpan) {
    labelSpan = document.createElement("span");
    labelSpan.className = "history-header-label";
    header.prepend(labelSpan);
  }

  labelSpan.textContent = language === "Chn" ? "历史记录" : "History";
}