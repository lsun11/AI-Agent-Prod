export function markdownToHtml(text: string): string {
  // Bold: **text**
  const bold = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  // Headings: # .. ######  (added, minimal change)
  const withHeadings = bold
    .replace(/^######\s+(.*)$/gm, "<h6>$1</h6>")
    .replace(/^#####\s+(.*)$/gm, "<h5>$1</h5>")
    .replace(/^####\s+(.*)$/gm, "<h4>$1</h4>")
    .replace(/^###\s+(.*)$/gm, "<h3>$1</h3>")
    .replace(/^##\s+(.*)$/gm, "<h2>$1</h2>")
    .replace(/^#\s+(.*)$/gm, "<h1>$1</h1>");

  // Keep your original list logic unchanged
  return withHeadings
    .replace(/^- (.*)/gm, "<li>$1</li>")
    .replace(/(<li>.*<\/li>)/g, "<ul>$1</ul>");
}
