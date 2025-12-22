// static/weather.ts
import {formatUtcOffsetLabel, buildPlaceLabel, weatherCodeToTexture} from "./weather_helpers.js"
import type {ReverseGeocodeResponse, WeatherTexture} from "./weather_helpers.js";

type Coords = { lat: number; lon: number };

type WeatherApiResponse = {
    timezone?: string;
    current?: {
        time?: string;
        temperature_2m?: number;
        apparent_temperature?: number;
        relative_humidity_2m?: number;
        precipitation?: number;
        weather_code?: number;
        wind_speed_10m?: number;
    };
    daily?: {
        time?: string[];
        weather_code?: number[];
        temperature_2m_max?: number[];
        temperature_2m_min?: number[];
        precipitation_probability_max?: number[];
    };
    source?: string;
};

function clamp(n: number, min: number, max: number) {
    return Math.max(min, Math.min(max, n));
}

function weatherCodeToTextAndIcon(code: number | undefined): { text: string; icon: string } {
    if (code === undefined || code === null) return {text: "Unknown", icon: "❓"};
    if (code === 0) return {text: "Clear", icon: "☀️"};
    if (code >= 1 && code <= 3) return {text: "Partly cloudy", icon: "⛅"};
    if (code === 45 || code === 48) return {text: "Fog", icon: "🌫️"};
    if (code >= 51 && code <= 57) return {text: "Drizzle", icon: "🌦️"};
    if (code >= 61 && code <= 67) return {text: "Rain", icon: "🌧️"};
    if (code >= 71 && code <= 77) return {text: "Snow", icon: "🌨️"};
    if (code >= 80 && code <= 82) return {text: "Showers", icon: "🌧️"};
    if (code >= 95) return {text: "Thunderstorm", icon: "⛈️"};
    return {text: "Mixed", icon: "🌦️"};
}

async function fetchJsonWithTimeout<T>(url: string, timeoutMs = 12000): Promise<T> {
    const controller = new AbortController();
    const t = window.setTimeout(() => controller.abort(), timeoutMs);
    try {
        const resp = await fetch(url, {signal: controller.signal, credentials: "same-origin"});
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        return (await resp.json()) as T;
    } finally {
        window.clearTimeout(t);
    }
}

/**
 * IMPORTANT: This class MUST receive the weather gadget root element,
 * and query elements inside it (no document.getElementById) so multiple gadgets work.
 */
export class WeatherGadget {
    private root: HTMLElement;

    // Elements inside the gadget (query within root)
    private metaEl: HTMLElement | null;
    private locEl: HTMLElement | null;
    private iconEl: HTMLElement | null;
    private tempEl: HTMLElement | null;
    private descEl: HTMLElement | null;
    private statsEl: HTMLElement | null;
    private updatedEl: HTMLElement | null;
    private detailsEl: HTMLElement | null;
    private refreshBtn: HTMLButtonElement | null;

    private coords: Coords | null = null;
    private timer: number | null = null;

    private tzEl: HTMLElement | null;
private forecastEl: HTMLElement | null;


    constructor(weatherGadgetRoot: HTMLElement) {
        this.root = weatherGadgetRoot;
        this.root.setAttribute("data-weather", "init");

        this.setMeta("Loading weather…");
        // Prefer data-weather hooks; fall back to IDs if you used them
        const q = <T extends Element>(sel: string) => this.root.querySelector(sel) as T | null;

        this.metaEl = q<HTMLElement>('[data-weather="meta"]') ?? q<HTMLElement>("#weather-meta");
        this.locEl = q<HTMLElement>('[data-weather="loc"]') ?? q<HTMLElement>("#weather-loc");
        this.iconEl = q<HTMLElement>('[data-weather="icon"]') ?? q<HTMLElement>("#weather-icon");
        this.tempEl = q<HTMLElement>('[data-weather="temp"]') ?? q<HTMLElement>("#weather-temp");
        this.descEl = q<HTMLElement>('[data-weather="desc"]') ?? q<HTMLElement>("#weather-desc");
        this.statsEl = q<HTMLElement>('[data-weather="stats"]') ?? q<HTMLElement>("#weather-stats");
        this.updatedEl = q<HTMLElement>('[data-weather="updated"]') ?? q<HTMLElement>("#weather-updated");
        this.detailsEl = q<HTMLElement>('[data-weather="details"]') ?? q<HTMLElement>("#weather-details");
        this.refreshBtn =
            (q<HTMLButtonElement>('[data-weather="refresh"]') ?? q<HTMLButtonElement>("#weather-refresh")) as
                | HTMLButtonElement
                | null;

        this.refreshBtn?.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            void this.refresh(true);
        });
        this.tzEl = q<HTMLElement>('[data-weather="tz"]');
        this.forecastEl = q<HTMLElement>('[data-weather="forecast"]');

        // Start immediately + every 30 minutes
        void this.refresh(false);
        this.timer = window.setInterval(() => void this.refresh(false), 30 * 60 * 1000);
    }

    public destroy(): void {
        if (this.timer !== null) {
            window.clearInterval(this.timer);
            this.timer = null;
        }
    }

    private isExpanded(): boolean {
        return this.root.classList.contains("gadget--expanded") || this.root.getAttribute("aria-expanded") === "true";
    }

    private setMeta(text: string) {
        // 1) update header meta element (if visible)
        if (this.metaEl) this.metaEl.textContent = text;

        // 2) update collapsed-sphere belt source
        this.root.setAttribute("data-meta", text);
    }

    private setTitleOnceIfMissing() {
        // Your sphere center title uses ::before attr(data-title)
        if (this.root.getAttribute("data-title")) return;
        const title =
            this.root.querySelector(".gadget-title")?.textContent?.trim() ||
            this.root.querySelector('[data-weather="title"]')?.textContent?.trim() ||
            "Weather";
        this.root.setAttribute("data-title", title);
    }

    private loadCachedCoords(): Coords | null {
        try {
            const raw = localStorage.getItem("weather.coords");
            if (!raw) return null;
            const o = JSON.parse(raw) as Coords;
            if (typeof o.lat === "number" && typeof o.lon === "number") return o;
            return null;
        } catch {
            return null;
        }
    }

    private cacheCoords(c: Coords) {
        try {
            localStorage.setItem("weather.coords", JSON.stringify(c));
            localStorage.setItem("weather.coords_ts", String(Date.now()));
        } catch {
            // ignore
        }
    }

    private async reverseGeocode(lat: number, lon: number): Promise<ReverseGeocodeResponse | null> {
        try {
            const params = new URLSearchParams({lat: String(lat), lon: String(lon)});
            return await fetchJsonWithTimeout<ReverseGeocodeResponse>(`/api/reverse_geocode?${params.toString()}`, 8000);
        } catch (e) {
            console.warn("[Weather] reverse geocode failed:", e);
            return null;
        }
    }

    private async tryBrowserGeolocation(): Promise<Coords> {
        if (!navigator.geolocation) throw new Error("Geolocation not supported");

        const pos = await new Promise<GeolocationPosition>((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, {
                enableHighAccuracy: false,
                timeout: 12000,
                maximumAge: 10 * 60 * 1000,
            });
        });
        console.log(pos);
        return {lat: pos.coords.latitude, lon: pos.coords.longitude};
    }

    private async tryGeoIpFallback(): Promise<Coords> {
        // hits your FastAPI /api/geoip
        const geo = await fetchJsonWithTimeout<{
            lat: number;
            lon: number;
            city?: string;
            region?: string;
            country?: string
        }>(
            "/api/geoip",
            8000,
        );
        if (typeof geo.lat !== "number" || typeof geo.lon !== "number") throw new Error("GeoIP did not return coords");
        return {lat: geo.lat, lon: geo.lon};
    }

    private getHardFallback(): Coords {
        // Last resort: Seoul (since your timezone/data is Asia/Seoul)
        return {lat: 37.5665, lon: 126.9780};
    }

    private async detectCoords(forcePrompt: boolean): Promise<Coords> {
        // reuse in-memory
        if (this.coords && !forcePrompt) return this.coords;

        // local cache
        const cached = this.loadCachedCoords();
        if (cached && !forcePrompt) {
            this.coords = cached;
            return cached;
        }

        this.setMeta("Detecting location…");

        // 1) Browser geolocation (best)
        try {
            const c = await this.tryBrowserGeolocation();
            this.coords = c;
            this.cacheCoords(c);
            return c;
        } catch (e) {
            // continue to fallback
            console.warn("[Weather] browser geolocation failed:", e);
        }

        // 2) GeoIP fallback (server-side IP lookup)
        try {
            this.setMeta("Using approximate location…");
            const c = await this.tryGeoIpFallback();
            this.coords = c;
            this.cacheCoords(c);
            return c;
        } catch (e) {
            console.warn("[Weather] geoip fallback failed:", e);
        }

        // 3) Hard fallback
        const c = this.getHardFallback();
        this.coords = c;
        this.cacheCoords(c);
        this.setMeta("Using default location…");
        return c;
    }

    private buildBackendWeatherUrl(lat: number, lon: number): string {
        const lang = (navigator.language || "en").toLowerCase().startsWith("zh") ? "zh" : "en";
        const params = new URLSearchParams({
            lat: String(lat),
            lon: String(lon),
            lang,
        });
        return `/api/weather?${params.toString()}`;
    }

    public async refresh(forcePrompt: boolean): Promise<void> {
        this.setTitleOnceIfMissing();

        try {
            const {lat, lon} = await this.detectCoords(forcePrompt);
            this.setMeta("Fetching weather…");

            // IMPORTANT: call your backend (not Open-Meteo directly)
            const url = this.buildBackendWeatherUrl(lat, lon);
            const data = await fetchJsonWithTimeout<WeatherApiResponse>(url, 12000);
            this.render7Day(data.daily);

            const cur = data.current ?? {};
            console.log(data);
            const {text, icon} = weatherCodeToTextAndIcon(cur.weather_code);
            const texture = weatherCodeToTexture(cur.weather_code);
            // Location label (simple; optionally enrich later with reverse geocode)
            // 1) place line
            const geo = await this.reverseGeocode(lat, lon);
            const placeLine = buildPlaceLabel(geo, lat, lon);
            if (this.locEl) this.locEl.textContent = placeLine;

            // 2) timezone line (separate element OR append with newline if your UI supports it)
            const tz = geo?.timezone || data.timezone; // prefer reverse-geocode timezone if present
            if (this.updatedEl) {
                // keep updatedEl as updated time; so use detailsEl or a dedicated timezone element if you have one
                // If you DON'T have a dedicated element, reuse detailsEl's first line.
            }

            if (this.tzEl) {
                const tz = geo?.timezone || data.timezone;
                const utcLabel = tz ? formatUtcOffsetLabel(tz) : "UTC";
                this.tzEl.textContent = tz ? `${utcLabel} • ${tz}` : utcLabel;
            }

            if (this.detailsEl) {
                const utcLabel = tz ? formatUtcOffsetLabel(tz) : "UTC";
                const tzLine = tz ? `${utcLabel} • ${tz}` : `${utcLabel}`;
                // Put timezone line at top when expanded; keep collapsed clean
                if (this.isExpanded()) {
                    const existing = this.detailsEl.innerHTML;
                    this.detailsEl.innerHTML = `<div class="weather-tz">${tzLine}</div>` + existing;
                }
            }

            if (this.iconEl) this.iconEl.textContent = icon;
            if (this.descEl) this.descEl.textContent = text;

            const t = cur.temperature_2m;
            if (this.tempEl) this.tempEl.textContent = typeof t === "number" ? `${t}°` : "—";

            // quick “chips”
            const chips: string[] = [];
            if (typeof cur.apparent_temperature === "number") chips.push(`Feels ${Math.round(cur.apparent_temperature)}°`);
            if (typeof cur.relative_humidity_2m === "number") chips.push(`Humidity ${Math.round(cur.relative_humidity_2m)}%`);
            if (typeof cur.wind_speed_10m === "number") chips.push(`Wind ${Math.round(cur.wind_speed_10m)}`);
            if (typeof cur.precipitation === "number") chips.push(`Precip ${cur.precipitation}`);

            if (this.statsEl) {
                this.statsEl.innerHTML = chips.map((c) => `<span class="weather-chip">${c}</span>`).join("");
            }

            // Only render details if expanded
            if (this.detailsEl) {
                if (!this.isExpanded()) {
                    this.detailsEl.innerHTML = "";
                } else {
                    const daily = data.daily ?? {};
                    const day0Max = daily.temperature_2m_max?.[0];
                    const day0Min = daily.temperature_2m_min?.[0];
                    const day0Pop = daily.precipitation_probability_max?.[0];
                    const day0Code = daily.weather_code?.[0];
                    const d0 = weatherCodeToTextAndIcon(day0Code);

                    const parts: string[] = [];
                    if (typeof day0Max === "number" && typeof day0Min === "number") {
                        parts.push(`Today:`);
                        parts.push(`Min ${Math.round(day0Min)}°  Max ${Math.round(day0Max)}°`);
                    }
                    if (typeof day0Pop === "number") parts.push(`Max precip chance: ${Math.round(clamp(day0Pop, 0, 100))}%`);
                    parts.push(`Outlook: ${d0.text} ${d0.icon}`);
                    if (data.source) parts.push(`Source: ${data.source}`);

                    this.detailsEl.innerHTML = parts.map((p) => `<div>${p}</div>`).join("");
                }
            }

            if (this.updatedEl) {
                const d = new Date();
                this.updatedEl.textContent = `Updated ${d.toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit"
                })}`;
            }
            this.root.dataset.weather = texture;
            // Collapsed meta (belt / header)
            const metaOneLine = typeof t === "number" ? `${icon} ${Math.round(t)}° • ${text}` : `${icon} ${text}`;
                    const el = this.root.querySelector(".weather-meta-line");
        if (el) el.textContent = placeLine;
            this.setMeta(metaOneLine);
        } catch (e: any) {
            const msg =
                e?.code === 1
                    ? "Location blocked — click Refresh"
                    : `Weather unavailable — ${String(e?.message ?? e)}`;

            this.setMeta(msg);

            if (this.detailsEl) this.detailsEl.innerHTML = "";
            if (this.statsEl) this.statsEl.innerHTML = "";
            if (this.locEl) this.locEl.textContent = "—";
            if (this.tempEl) this.tempEl.textContent = "—";
            if (this.descEl) this.descEl.textContent = "—";
            if (this.iconEl) this.iconEl.textContent = "❓";
            if (this.updatedEl) this.updatedEl.textContent = "";
            if (this.forecastEl) this.forecastEl.innerHTML = "";
        }
    }

    private formatDow(dateStr: string): string {
  // Open-Meteo daily.time is "YYYY-MM-DD"
  const d = new Date(`${dateStr}T00:00:00`);
  return d.toLocaleDateString(undefined, { weekday: "short" });
}

private render7Day(daily: WeatherApiResponse["daily"] | undefined): void {
  if (!this.forecastEl) return;

  // Only show in expanded state
  if (!this.isExpanded()) {
    this.forecastEl.innerHTML = "";
    return;
  }

  const times = daily?.time ?? [];
  const codes = daily?.weather_code ?? [];
  const tmax = daily?.temperature_2m_max ?? [];
  const tmin = daily?.temperature_2m_min ?? [];
  const pop = daily?.precipitation_probability_max ?? [];

  const n = Math.min(7, times.length, codes.length, tmax.length, tmin.length);
  if (n <= 0) {
    this.forecastEl.innerHTML = "";
    return;
  }

  // Week range for relative bars
  let weekMin = Number.POSITIVE_INFINITY;
  let weekMax = Number.NEGATIVE_INFINITY;
  for (let i = 0; i < n; i++) {
    if (typeof tmin[i] === "number") weekMin = Math.min(weekMin, tmin[i]!);
    if (typeof tmax[i] === "number") weekMax = Math.max(weekMax, tmax[i]!);
  }
  const span = Math.max(1, weekMax - weekMin);

  const cards: string[] = [];
  for (let i = 0; i < n; i++) {
    const code = codes[i];
    const { text, icon } = weatherCodeToTextAndIcon(code);

    const minV = typeof tmin[i] === "number" ? Math.round(tmin[i]!) : NaN;
    const maxV = typeof tmax[i] === "number" ? Math.round(tmax[i]!) : NaN;

    const popV = typeof pop[i] === "number" ? Math.round(clamp(pop[i]!, 0, 100)) : null;

    // Bar position/width based on min/max within week range
    const leftPct = typeof tmin[i] === "number" ? ((tmin[i]! - weekMin) / span) * 100 : 0;
    const widthPct =
      typeof tmin[i] === "number" && typeof tmax[i] === "number"
        ? ((tmax[i]! - tmin[i]!) / span) * 100
        : 0;

    cards.push(`
      <div class="weather-day">
        <div class="weather-day-top">
          <div class="weather-dow">${this.formatDow(times[i]!)}</div>
          <div class="weather-icon" aria-hidden="true">${icon}</div>
        </div>

        <div class="weather-cond" title="${text}">${text}</div>

        <div class="weather-temps">
          <div class="weather-min">${Number.isFinite(minV) ? `${minV}°` : "—"}</div>
          <div class="weather-max">${Number.isFinite(maxV) ? `${maxV}°` : "—"}</div>
        </div>

        <div class="weather-bar" aria-hidden="true">
          <span style="margin-left:${leftPct.toFixed(1)}%; width:${Math.max(2, widthPct).toFixed(1)}%"></span>
        </div>

        <div class="weather-pop">
          <span aria-hidden="true">💧</span>
          <span>${popV === null ? "—" : `${popV}%`}</span>
        </div>
      </div>
    `);
  }

  this.forecastEl.innerHTML = cards.join("");
}

}
