// static/chat-ui.ts
import { DROPDOWN_OPTIONS_BY_ID } from "./configs.js";
import { markdownToHtml } from "./markdown.js";
import { mapLanguageValue, translateLabel, getGreetingText, getFollowupText, applyInterfaceLanguage, refreshDropdownLabels } from "./language.js";
import { RECOMMENDATION_STARTERS } from "./types.js";
export class ChatUI {
    constructor() {
        this.suggestionGrid = null;
        this.currentSuggestionGrid = null;
        this.currentTopicKey = null;
        this.isThinking = false;
        this.language = "Chn";
        this.latestCompaniesVisual = [];
        const formEl = document.getElementById("chat-form");
        const inputEl = document.getElementById("chat-input");
        const messagesEl = document.getElementById("messages");
        if (!(formEl instanceof HTMLFormElement)) {
            throw new Error("chat-form element not found or not a form");
        }
        if (!(inputEl instanceof HTMLInputElement)) {
            throw new Error("chat-input element not found or not an input");
        }
        if (!(messagesEl instanceof HTMLDivElement)) {
            throw new Error("messages element not found or not a div");
        }
        this.form = formEl;
        this.input = inputEl;
        this.messagesEl = messagesEl;
        const button = this.form.querySelector("button");
        if (!(button instanceof HTMLButtonElement)) {
            throw new Error("Submit button not found");
        }
        this.submitButton = button;
        this.attachListeners();
        // dropdowns
        const languageSelectEl = this.addDropDown("language-select");
        if (!languageSelectEl) {
            throw new Error("Failed to create Language Select");
        }
        const modelSelectEl = this.addDropDown("model-select");
        if (!modelSelectEl) {
            throw new Error("Failed to create model-select dropdown");
        }
        const humanizationSelectEl = this.addDropDown("humanization");
        if (!humanizationSelectEl) {
            throw new Error("Failed to create humanization dropdown");
        }
        this.languageSelect = languageSelectEl;
        this.modelSelect = modelSelectEl;
        this.humanizationSelect = humanizationSelectEl;
        // language setup
        this.language = mapLanguageValue(this.languageSelect.value);
        this.updateInterfaceLanguage();
        this.addGreeting(this.language);
        this.fetchSuggestions("fast").catch((err) => console.error("Failed to fetch suggestions:", err));
        this.languageSelect.addEventListener("change", () => {
            this.language = mapLanguageValue(this.languageSelect.value);
            this.updateInterfaceLanguage();
            refreshDropdownLabels(this.language);
            const switchedMsg = this.language === "Chn"
                ? "🌐 已切换到中文界面"
                : "🌐 Switched to English interface";
            this.addMessage(switchedMsg, "greeting");
            this.addGreeting(this.language);
            this.fetchSuggestions().catch((err) => console.error("Failed to fetch suggestions:", err));
        });
    }
    async fetchSuggestions(mode = "slow") {
        const params = new URLSearchParams({ language: this.language, mode: mode });
        const res = await fetch(`/suggestions?${params.toString()}`, { method: "GET" });
        if (!res.ok) {
            console.warn("Suggestions request failed:", res.statusText);
            return;
        }
        const data = await res.json();
        if (!data.suggestions || !Array.isArray(data.suggestions)) {
            return;
        }
        if (this.currentSuggestionGrid) {
            this.currentSuggestionGrid.remove();
            this.currentSuggestionGrid = null;
        }
        const grid = document.createElement("div");
        grid.className = "suggestion-grid";
        this.currentSuggestionGrid = grid;
        // Append directly under the most recent message (which you just added)
        this.messagesEl.appendChild(grid);
        // Now add the suggestion bubbles into THIS grid
        data.suggestions.forEach((q) => {
            if (typeof q === "string" && q.trim()) {
                this.addSuggestionBubble(q.trim(), grid);
            }
        });
        // Scroll to bottom so the user sees them
        this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
    }
    addSuggestionBubble(text, grid) {
        const div = document.createElement("div");
        div.className = "message suggestion";
        div.textContent = text;
        // Click to autofill input
        div.addEventListener("click", () => {
            this.input.value = text;
            this.input.focus();
        });
        grid.appendChild(div);
    }
    updateInterfaceLanguage() {
        const titleEl = document.getElementById("app-title");
        applyInterfaceLanguage(this.language, this.input, this.submitButton, titleEl);
    }
    addGreeting(language) {
        const greeting = getGreetingText(language);
        this.addMessage(greeting, "greeting");
    }
    addFollowupMsg() {
        const followup = getFollowupText(this.language);
        this.addMessage(followup, "greeting");
    }
    attachListeners() {
        this.form.addEventListener("submit", (event) => {
            event.preventDefault();
            void this.handleSubmit();
        });
    }
    extractWebsiteUrl(text) {
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
    addMessage(text, sender, url) {
        const div = document.createElement("div");
        div.className = `message ${sender}`;
        // render markdown → HTML
        div.innerHTML = markdownToHtml(text);
        if (sender === "bot" && url) {
            div.classList.add("clickable");
            div.addEventListener("click", () => {
                window.open(url, "_blank");
            });
        }
        this.messagesEl.appendChild(div);
        this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
    }
    addDownloadButton(url, object) {
        // Create a NEW container for this answer's download button(s)
        const downloadContainer = document.createElement("div");
        downloadContainer.className = "download-container";
        const button = document.createElement("button");
        button.type = "button";
        button.className = "download-button";
        button.textContent =
            this.language === "Eng"
                ? "Download summary (" + object + ")"
                : "下载总结 (" + object + ")";
        button.addEventListener("click", () => {
            window.open(url, "_blank");
        });
        downloadContainer.appendChild(button);
        // Append THIS container right after the current answer's bubbles
        this.messagesEl.appendChild(downloadContainer);
        this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
    }
    addDropDown(selectId) {
        const dropdownContainer = document.getElementById("dropdown-container");
        if (!dropdownContainer) {
            console.error("dropdown-container not found");
            return null;
        }
        const options = DROPDOWN_OPTIONS_BY_ID[selectId];
        if (!options) {
            console.warn(`No dropdown options configured for selectId="${selectId}"`);
            return null;
        }
        const select = document.createElement("select");
        select.id = selectId;
        select.className = selectId;
        for (const opt of options) {
            const optionEl = document.createElement("option");
            optionEl.value = opt.value;
            optionEl.dataset.labelKey = opt.label;
            optionEl.textContent = translateLabel(opt.label, this.language);
            if (opt.disabled)
                optionEl.disabled = true;
            if (opt.selected)
                optionEl.selected = true;
            select.appendChild(optionEl);
        }
        dropdownContainer.appendChild(select);
        return select;
    }
    startThinking() {
        if (this.isThinking)
            return;
        this.isThinking = true;
        document.body.classList.add("thinking");
    }
    stopThinking() {
        if (!this.isThinking)
            return;
        this.isThinking = false;
        document.body.classList.remove("thinking");
    }
    updateTitle(topicLabel) {
        const titleEl = document.getElementById("app-title");
        if (titleEl) {
            titleEl.textContent = `AI Research Assistant — ${topicLabel}`;
        }
        document.title = `AI Research: ${topicLabel}`;
    }
    updateBackground(topicKey) {
        if (this.currentTopicKey) {
            document.body.classList.remove(`topic-bg-${this.currentTopicKey}`);
        }
        document.body.classList.add(`topic-bg-${topicKey}`);
        this.currentTopicKey = topicKey;
    }
    splitReplyIntoBubbles(reply) {
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
            // if (trimmed.startsWith("**Recommendations") || trimmed.startsWith("**推荐"))
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
    addCompanyBubble(text, company) {
        const wrapper = document.createElement("div");
        // keep the same base classes so CSS stays the same as other bot bubbles
        wrapper.className = "message bot company-bubble";
        // Make sure we can layer children inside
        wrapper.style.position = "relative";
        wrapper.style.overflow = "hidden";
        // --- Logo background overlay (tiled, semi-transparent) ---
        if (company.logo_url) {
            const bg = document.createElement("div");
            bg.className = "company-logo-bg";
            bg.style.position = "absolute";
            bg.style.inset = "0";
            bg.style.zIndex = "0";
            bg.style.pointerEvents = "none"; // don't block clicks
            bg.style.backgroundImage = `url(${company.logo_url})`;
            bg.style.backgroundRepeat = "repeat"; // tiled
            bg.style.backgroundPosition = "center";
            bg.style.backgroundSize = "240px 240px"; // tweak as you like
            bg.style.opacity = "0.08"; // semi-transparent
            wrapper.appendChild(bg);
        }
        // --- Foreground content (keeps original bubble look) ---
        const inner = document.createElement("div");
        inner.className = "company-bubble-inner";
        inner.style.position = "relative";
        inner.style.zIndex = "1";
        // Optional: show company name as a small header
        if (company.name) {
            const nameEl = document.createElement("div");
            nameEl.className = "company-name";
            nameEl.textContent = company.name;
            inner.appendChild(nameEl);
        }
        const bodyEl = document.createElement("div");
        bodyEl.className = "company-body";
        bodyEl.innerHTML = markdownToHtml(text); // same markdown rendering as other bubbles
        inner.appendChild(bodyEl);
        wrapper.appendChild(inner);
        // Make bubble clickable to open website if available
        if (company.website) {
            wrapper.classList.add("clickable");
            wrapper.addEventListener("click", () => {
                window.open(company.website, "_blank");
            });
        }
        this.messagesEl.appendChild(wrapper);
        this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
    }
    async handleSubmit() {
        const text = this.input.value.trim();
        if (!text)
            return;
        this.addMessage(text, "user");
        this.input.value = "";
        this.input.focus();
        this.submitButton.disabled = true;
        try {
            const model = this.modelSelect.value || "gpt-4.1-mini";
            const temperature = this.humanizationSelect.value || "0.1";
            const params = new URLSearchParams({ message: text, model, temperature });
            const es = new EventSource(`/chat_stream?${params.toString()}`);
            this.currentEventSource = es;
            const thinkingMsg = this.language === "Chn"
                ? "🤔 正在思考，请稍候…"
                : "🤔 Start thinking, please wait...";
            this.addMessage(thinkingMsg, "greeting");
            es.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === "topic") {
                        const topicLabel = data.topic_label;
                        const topicKey = data.topic_key;
                        const topicDomain = data.topic_domain;
                        this.updateTitle(topicLabel);
                        this.updateBackground(topicDomain);
                        this.startThinking();
                        return;
                    }
                    if (data.type === "log") {
                        this.addMessage(data.message, "thinking");
                        return;
                    }
                    if (data.type === "final") {
                        const bubbles = this.splitReplyIntoBubbles(data.reply);
                        // NEW: read visual info from backend
                        const companiesVisual = (data.companies_visual || []);
                        this.latestCompaniesVisual = companiesVisual;
                        for (let i = 0; i < bubbles.length; i++) {
                            const isFirst = i === 0;
                            const isLast = i === bubbles.length - 1;
                            // Middle bubbles: show company bubble with logo/color
                            if (!isFirst && !isLast) {
                                const companyIndex = i - 1; // bubble 1 ↔ company 0, bubble 2 ↔ company 1, ...
                                const company = companiesVisual[companyIndex];
                                if (company) {
                                    // @ts-ignore
                                    this.addCompanyBubble(bubbles[i], company);
                                }
                                else {
                                    // Fallback if we don't have a matching company
                                    // @ts-ignore
                                    const url = this.extractWebsiteUrl(bubbles[i]);
                                    // @ts-ignore
                                    this.addMessage(bubbles[i], "bot", url);
                                }
                                continue;
                            }
                            // First and last bubble: normal bot messages
                            const style = "bot-first";
                            // @ts-ignore
                            const url = this.extractWebsiteUrl(bubbles[i]);
                            // @ts-ignore
                            this.addMessage(bubbles[i], style, url);
                        }
                        if (data.download_url) {
                            const object = this.language === "Eng" ? "document" : "文档";
                            this.addDownloadButton(data.download_url, object);
                        }
                        if (data.slides_download_url) {
                            const object = this.language === "Eng" ? "slides" : "演示文稿";
                            this.addDownloadButton(data.slides_download_url, object);
                        }
                        es.close();
                        this.stopThinking();
                        this.addFollowupMsg();
                        this.fetchSuggestions().catch((err) => console.error("Failed to fetch suggestions:", err));
                        this.submitButton.disabled = false;
                    }
                }
                catch (e) {
                    console.error("Error parsing SSE data", e, event.data);
                }
            };
            es.onerror = (err) => {
                console.error("SSE error:", err);
                this.addMessage("Error: connection lost.", "bot");
                es.close();
                this.submitButton.disabled = false;
            };
        }
        catch (error) {
            console.error(error);
            const msg = error instanceof Error ? error.message : String(error);
            this.addMessage(`Network error: ${msg}`, "bot");
            this.submitButton.disabled = false;
        }
    }
}
//# sourceMappingURL=chat-ui.js.map