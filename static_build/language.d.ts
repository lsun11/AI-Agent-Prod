import type { LanguageCode } from "./types.js";
export declare function mapLanguageValue(value: string): LanguageCode;
export declare function translateLabel(labelKey: string, language: LanguageCode): string;
export declare function getGreetingText(language: LanguageCode): string;
export declare function getFollowupText(language: LanguageCode): string;
export declare function applyInterfaceLanguage(language: LanguageCode, input: HTMLInputElement, submitButton: HTMLButtonElement, titleEl: HTMLElement | null): void;
export declare function refreshDropdownLabels(language: LanguageCode): void;
//# sourceMappingURL=language.d.ts.map