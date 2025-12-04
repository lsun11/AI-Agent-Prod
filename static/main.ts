import {ChatUI} from "./chat-ui.js";
import {initHistoryPanel} from "./history.js";

document.addEventListener("DOMContentLoaded", () => {
    new ChatUI();
    void initHistoryPanel();
});