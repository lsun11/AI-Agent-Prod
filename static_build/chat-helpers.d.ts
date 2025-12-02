import { type LanguageCode } from "./types.js";
export interface CompanyVisual {
    name: string | null;
    website: string | null;
    logo_url: string | null;
    primary_color: string | null;
    brand_colors: Record<string, string> | null;
}
export interface ResourceVisual {
    title: string | null;
    url: string | null;
    logo_url: string | null;
    primary_color: string | null;
    brand_colors: Record<string, string> | null;
}
/**
 * Extracts a website URL from a chunk of markdown/text.
 */
export declare function extractWebsiteUrl(text: string): string | undefined;
/**
 * Splits the LLM reply into logical “bubbles”.
 * (Same logic you had in ChatUI before, just extracted.)
 */
export declare function splitReplyIntoBubbles(reply: string): string[];
/**
 * Builds a company bubble DOM node with a tiled, semi-transparent logo background.
 */
export declare function createCompanyBubbleElement(text: string, company: CompanyVisual): HTMLDivElement;
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
export declare function createDownloadButtonElement(url: string, object: string, language: LanguageCode, multiFormat?: boolean): HTMLDivElement;
export declare function createDownloadButtonElement(urls: {
    pdf: string;
    docx: string;
    txt: string;
}, object: string, language: LanguageCode, multiFormat: true): HTMLDivElement;
//# sourceMappingURL=chat-helpers.d.ts.map