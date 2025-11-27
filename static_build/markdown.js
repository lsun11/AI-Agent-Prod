export function markdownToHtml(text) {
    const bold = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    return bold
        .replace(/^- (.*)/gm, "<li>$1</li>")
        .replace(/(<li>.*<\/li>)/g, "<ul>$1</ul>");
}
//# sourceMappingURL=markdown.js.map