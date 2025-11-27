const LABEL_TRANSLATIONS = {
    "Choose AI model…": {
        Eng: "Choose AI model…",
        Chn: "选择 AI 模型…",
    },
    "Humanization Level...": {
        Eng: "Humanization Level...",
        Chn: "人性化程度…",
    },
};
export function mapLanguageValue(value) {
    if (value === "Chn" || value === "zh-CN" || value === "zh") {
        return "Chn";
    }
    return "Eng";
}
export function translateLabel(labelKey, language) {
    const langMap = LABEL_TRANSLATIONS[labelKey];
    if (langMap && langMap[language]) {
        return langMap[language];
    }
    return labelKey;
}
export function getGreetingText(language) {
    const greetingEng = "🤘Hello! I'm your AI Research Assistant for computer developing.\n\n" +
        "Ask me anything about: \n " +
        "📦 developer tools and software,\n " +
        "🏢 career as a developer,\n " +
        "💻 and any other dev related topics!\n\n" +
        "Just type your question below to get started.";
    const greetingChn = "🤘你好\n\n" +
        "可以咨询我任何关于: \n " +
        "📦 开发者工具和软件,\n " +
        "🏢 程序员职业发展,\n " +
        "💻 和其他任何计算机相关的问题\n\n" +
        "请在下面输入你的问题";
    return language === "Eng" ? greetingEng : greetingChn;
}
export function getFollowupText(language) {
    const followupEng = "🤘Please let me know if you need anything else.";
    const followupChn = "🤘如果还有其他问题，欢迎继续提问。";
    return language === "Chn" ? followupChn : followupEng;
}
export function applyInterfaceLanguage(language, input, submitButton, titleEl) {
    if (language === "Chn") {
        input.placeholder = "请输入你的问题…";
        submitButton.textContent = "发送";
        if (titleEl) {
            titleEl.textContent = "AI 研究助手 — 计算机开发";
        }
        document.title = "AI 研究助手";
    }
    else {
        input.placeholder = "Ask me anything about dev tools, careers, etc…";
        submitButton.textContent = "Send";
        if (titleEl) {
            titleEl.textContent = "AI Research Assistant — Developer Topics";
        }
        document.title = "AI Research Assistant";
    }
}
export function refreshDropdownLabels(language) {
    const ids = ["model-select", "humanization"]; // add "language-select" if you want to translate that too
    for (const id of ids) {
        const select = document.getElementById(id);
        if (!select)
            continue;
        for (const option of Array.from(select.options)) {
            const key = option.dataset.labelKey;
            if (key) {
                option.textContent = translateLabel(key, language);
            }
        }
    }
}
//# sourceMappingURL=language.js.map