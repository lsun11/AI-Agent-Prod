// static/chat-ui.ts
import { DROPDOWN_OPTIONS_BY_ID } from "./configs.js";
import { markdownToHtml } from "./markdown.js";
import { mapLanguageValue, translateLabel, getGreetingText, getFollowupText, applyInterfaceLanguage, refreshDropdownLabels } from "./language.js";
import { extractWebsiteUrl, splitReplyIntoBubbles, createCompanyBubbleElement, createDownloadButtonElement, } from "./chat-helpers.js";
import { setHistoryHeaderLanguage } from "./history.js";
const STORAGE_KEYS = {
    language: "ai_research_language",
    model: "ai_research_model",
    humanization: "ai_research_humanization",
};
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
        this.restorePersistedSettings();
        // language setup
        this.language = mapLanguageValue(this.languageSelect.value);
        this.updateInterfaceLanguage();
        this.addGreeting(this.language);
        this.fetchSuggestions("fast").catch((err) => console.error("Failed to fetch suggestions:", err));
        setHistoryHeaderLanguage(this.language);
        this.languageSelect.addEventListener("change", () => {
            this.language = mapLanguageValue(this.languageSelect.value);
            try {
                window.localStorage.setItem(STORAGE_KEYS.language, this.languageSelect.value);
            }
            catch (err) {
                console.warn("Failed to persist language setting:", err);
            }
            this.updateInterfaceLanguage();
            refreshDropdownLabels(this.language);
            // ✅ keep history header in sync without wiping the button
            setHistoryHeaderLanguage(this.language);
            const switchedMsg = this.language === "Chn"
                ? "🌐 已切换到中文界面"
                : "🌐 Switched to English interface";
            this.addMessage(switchedMsg, "greeting");
            this.addGreeting(this.language);
            this.fetchSuggestions().catch((err) => console.error("Failed to fetch suggestions:", err));
        });
        // 🔹 Persist model selection
        this.modelSelect.addEventListener("change", () => {
            try {
                window.localStorage.setItem(STORAGE_KEYS.model, this.modelSelect.value);
            }
            catch (err) {
                console.warn("Failed to persist model setting:", err);
            }
        });
        // 🔹 Persist humanization (temperature) selection
        this.humanizationSelect.addEventListener("change", () => {
            try {
                window.localStorage.setItem(STORAGE_KEYS.humanization, this.humanizationSelect.value);
            }
            catch (err) {
                console.warn("Failed to persist humanization setting:", err);
            }
        });
    }
    restorePersistedSettings() {
        try {
            const savedLanguage = window.localStorage.getItem(STORAGE_KEYS.language);
            const savedModel = window.localStorage.getItem(STORAGE_KEYS.model);
            const savedHumanization = window.localStorage.getItem(STORAGE_KEYS.humanization);
            if (savedLanguage && this.languageSelect) {
                const option = Array.from(this.languageSelect.options).find((opt) => opt.value === savedLanguage);
                if (option) {
                    this.languageSelect.value = savedLanguage;
                }
            }
            if (savedModel && this.modelSelect) {
                const option = Array.from(this.modelSelect.options).find((opt) => opt.value === savedModel);
                if (option) {
                    this.modelSelect.value = savedModel;
                }
            }
            if (savedHumanization && this.humanizationSelect) {
                const option = Array.from(this.humanizationSelect.options).find((opt) => opt.value === savedHumanization);
                if (option) {
                    this.humanizationSelect.value = savedHumanization;
                }
            }
        }
        catch (err) {
            console.warn("Failed to restore persisted settings:", err);
        }
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
                        const bubbles = splitReplyIntoBubbles(data.reply);
                        // read visual info from backend
                        const companiesVisual = (data.companies_visual || []);
                        this.latestCompaniesVisual = companiesVisual;
                        for (let i = 0; i < bubbles.length; i++) {
                            const isFirst = i === 0;
                            const isLast = i === bubbles.length - 1;
                            // Middle bubbles → company bubbles
                            if (!isFirst && !isLast) {
                                const companyIndex = i - 1; // bubble 1 ↔ company 0, etc.
                                const company = companiesVisual[companyIndex];
                                if (company) {
                                    // @ts-ignore
                                    const bubbleEl = createCompanyBubbleElement(bubbles[i], company);
                                    this.messagesEl.appendChild(bubbleEl);
                                    this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
                                }
                                else {
                                    // @ts-ignore
                                    const url = extractWebsiteUrl(bubbles[i]);
                                    // @ts-ignore
                                    this.addMessage(bubbles[i], "bot", url);
                                }
                                continue;
                            }
                            // First and last bubble: normal bot messages
                            const style = "bot-first";
                            // @ts-ignore
                            const url = extractWebsiteUrl(bubbles[i]);
                            // @ts-ignore
                            this.addMessage(bubbles[i], style, url);
                        }
                        // Download buttons using helper
                        if (data.download_pdf_url || data.download_docx_url || data.download_txt_url) {
                            const object = this.language === "Eng" ? "document" : "文档";
                            const el = createDownloadButtonElement({
                                pdf: data.download_pdf_url,
                                docx: data.download_docx_url,
                                txt: data.download_txt_url
                            }, object, this.language, true // 👈 enable multi-format menu for the document
                            );
                            this.messagesEl.appendChild(el);
                            this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
                        }
                        if (data.slides_download_url) {
                            const object = this.language === "Eng" ? "slides" : "演示文稿";
                            const el = createDownloadButtonElement(data.slides_download_url, object, this.language // 👈 leave default (single-click)
                            );
                            this.messagesEl.appendChild(el);
                            this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
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