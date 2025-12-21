import { type LanguageCode } from "../../constants/types.js";
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
export interface DownloadFormatUrls {
    pdf?: string | null;
    docx?: string | null;
    txt?: string | null;
    pptx?: string | null;
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
type PreviewFormat = "pdf" | "txt" | "pptx";
interface PreviewConfig {
    title: string;
    urls: DownloadFormatUrls;
    preferred?: PreviewFormat;
}
/**
 * Open / update the side preview panel for pdf/txt/pptx.
 */
export declare function openFilePreview(config: PreviewConfig): void;
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
export declare function createDownloadButtonElement(urlsOrUrl: string | DownloadFormatUrls, object: string, language: LanguageCode, enableMultiFormatMenu?: boolean): HTMLDivElement;
export {};
//# sourceMappingURL=chat-helpers.d.ts.map