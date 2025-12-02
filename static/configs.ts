export type SelectOption = {
  value: string;
  label: string;
  disabled?: boolean;
  selected?: boolean;
};

// Models dropdown options
const MODEL_OPTIONS: SelectOption[] = [
  { value: "", label: "Choose AI model…", disabled: true, selected: true },
    { value: "gpt-4.1-mini", label: "GPT 4.1 Mini (default)" },
    { value: "gpt-4o", label: "GPT 4o" },
    { value: "gpt-4o-mini", label: "GPT 4o Mini" },
  { value: "gpt-4.1", label: "GPT 4.1" },
  { value: "gpt-5", label: "GPT 5" },
  { value: "gpt-5-mini", label: "GPT 5 Mini" },
  { value: "gpt-5.1", label: "GPT 5.1" },
    {value: 'claude-sonnet-4-5-20250929', label: "Claude Sonnet 4.5"},
    {value: "claude-haiku-4-5-20251001", label: "Claude Haiku 4.5"},
    { value: "deepseek-chat", label: "Deepseek V3" },
    { value: "gemini-3-pro-preview", label: "Gemini 3" },
    { value: "gemini-2.5-flash", label: "Gemini 2.5 Flash" },
    { value: "gemini-2.5-flash-lite", label: "Gemini 2.5 Flash Lite" },
];

// Humanization dropdown options
const HUMANIZATION_OPTIONS: SelectOption[] = [
  { value: "", label: "Humanization Level...", disabled: true, selected: true },
  // value = internal key (e.g. temp_0p1), label = what user sees
  { value: "0.1", label: "Somewhat Robotic (default)" },
  { value: "0.01", label: "Very Robotic" },
  { value: "0.3", label: "Human-ish" },
  { value: "0.5", label: "Very Human" },
];

const LANGUAGE_OPTIONS: SelectOption[] = [
    { value: "Chn", label: "中文" },
    { value: "Eng", label: "English" },
]

// Map select.id -> option list
export const DROPDOWN_OPTIONS_BY_ID: Record<string, SelectOption[]> = {
  "model-select": MODEL_OPTIONS,
  humanization: HUMANIZATION_OPTIONS,
    "language-select": LANGUAGE_OPTIONS,
};