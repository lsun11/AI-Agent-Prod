// static/weather.ts
function clamp(n, min, max) {
    return Math.max(min, Math.min(max, n));
}
function weatherCodeToTextAndIcon(code) {
    if (code === undefined || code === null)
        return { text: "Unknown", icon: "❓" };
    // Minimal but useful mapping
    if (code === 0)
        return { text: "Clear", icon: "☀️" };
    if (code >= 1 && code <= 3)
        return { text: "Partly cloudy", icon: "⛅" };
    if (code === 45 || code === 48)
        return { text: "Fog", icon: "🌫️" };
    if (code >= 51 && code <= 57)
        return { text: "Drizzle", icon: "🌦️" };
    if (code >= 61 && code <= 67)
        return { text: "Rain", icon: "🌧️" };
    if (code >= 71 && code <= 77)
        return { text: "Snow", icon: "🌨️" };
    if (code >= 80 && code <= 82)
        return { text: "Showers", icon: "🌧️" };
    if (code >= 95)
        return { text: "Thunderstorm", icon: "⛈️" };
    return { text: "Mixed", icon: "🌦️" };
}
async function fetchJsonWithTimeout(url, timeoutMs = 12000) {
    const controller = new AbortController();
    const t = window.setTimeout(() => controller.abort(), timeoutMs);
    try {
        const resp = await fetch(url, { signal: controller.signal });
        if (!resp.ok)
            throw new Error(`HTTP ${resp.status}`);
        return (await resp.json());
    }
    finally {
        window.clearTimeout(t);
    }
}
export class WeatherGadget {
    constructor(gadget) {
        var _a;
        this.coords = null;
        this.timer = null;
        this.gadget = gadget;
        this.metaEl = document.getElementById("weather-meta");
        this.locEl = document.getElementById("weather-loc");
        this.iconEl = document.getElementById("weather-icon");
        this.tempEl = document.getElementById("weather-temp");
        this.descEl = document.getElementById("weather-desc");
        this.statsEl = document.getElementById("weather-stats");
        this.updatedEl = document.getElementById("weather-updated");
        this.detailsEl = document.getElementById("weather-details");
        this.refreshBtn = document.getElementById("weather-refresh");
        (_a = this.refreshBtn) === null || _a === void 0 ? void 0 : _a.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            void this.refresh(true);
        });
        // start immediately + every 30 minutes
        void this.refresh(false);
        this.timer = window.setInterval(() => void this.refresh(false), 30 * 60 * 1000);
    }
    destroy() {
        if (this.timer !== null) {
            window.clearInterval(this.timer);
            this.timer = null;
        }
    }
    setMeta(text) {
        if (this.metaEl)
            this.metaEl.textContent = text;
    }
    loadCachedCoords() {
        try {
            const raw = localStorage.getItem("weather.coords");
            if (!raw)
                return null;
            const o = JSON.parse(raw);
            if (typeof o.lat === "number" && typeof o.lon === "number")
                return o;
            return null;
        }
        catch (_a) {
            return null;
        }
    }
    cacheCoords(c) {
        try {
            localStorage.setItem("weather.coords", JSON.stringify(c));
            localStorage.setItem("weather.coords_ts", String(Date.now()));
        }
        catch (_a) {
            // ignore
        }
    }
    async detectCoords(forcePrompt) {
        // If we already have coords and not forcing, reuse
        if (this.coords && !forcePrompt)
            return this.coords;
        const cached = this.loadCachedCoords();
        if (cached && !forcePrompt) {
            this.coords = cached;
            return cached;
        }
        if (!navigator.geolocation)
            throw new Error("Geolocation not supported");
        this.setMeta("Detecting location…");
        const pos = await new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, {
                enableHighAccuracy: false,
                timeout: 12000,
                maximumAge: 10 * 60 * 1000,
            });
        });
        const c = { lat: pos.coords.latitude, lon: pos.coords.longitude };
        this.coords = c;
        this.cacheCoords(c);
        return c;
    }
    buildForecastUrl(lat, lon) {
        var _a;
        const useF = (_a = navigator.language) === null || _a === void 0 ? void 0 : _a.toLowerCase().startsWith("en-us");
        const params = new URLSearchParams({
            latitude: String(lat),
            longitude: String(lon),
            timezone: "auto",
            // current snapshot
            current: [
                "temperature_2m",
                "apparent_temperature",
                "relative_humidity_2m",
                "precipitation",
                "weather_code",
                "wind_speed_10m",
            ].join(","),
            // daily summary for “details”
            daily: [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_probability_max",
            ].join(","),
        });
        if (useF) {
            params.set("temperature_unit", "fahrenheit");
            params.set("wind_speed_unit", "mph");
        }
        return `https://api.open-meteo.com/v1/forecast?${params.toString()}`;
    }
    async refresh(forcePrompt) {
        var _a, _b, _c, _d, _e, _f, _g;
        try {
            const { lat, lon } = await this.detectCoords(forcePrompt);
            this.setMeta("Fetching weather…");
            const url = this.buildForecastUrl(lat, lon);
            const data = await fetchJsonWithTimeout(url);
            const cur = (_a = data.current) !== null && _a !== void 0 ? _a : {};
            const { text, icon } = weatherCodeToTextAndIcon(cur.weather_code);
            // Location label (keep simple + reliable)
            const locLabel = `Lat ${lat.toFixed(2)}, Lon ${lon.toFixed(2)}${data.timezone ? ` • ${data.timezone}` : ""}`;
            if (this.locEl)
                this.locEl.textContent = locLabel;
            if (this.iconEl)
                this.iconEl.textContent = icon;
            if (this.descEl)
                this.descEl.textContent = text;
            const t = cur.temperature_2m;
            if (this.tempEl)
                this.tempEl.textContent = typeof t === "number" ? `${Math.round(t)}°` : "—";
            // quick chips
            const chips = [];
            if (typeof cur.apparent_temperature === "number")
                chips.push(`Feels ${Math.round(cur.apparent_temperature)}°`);
            if (typeof cur.relative_humidity_2m === "number")
                chips.push(`Humidity ${Math.round(cur.relative_humidity_2m)}%`);
            if (typeof cur.wind_speed_10m === "number")
                chips.push(`Wind ${Math.round(cur.wind_speed_10m)}`);
            if (typeof cur.precipitation === "number")
                chips.push(`Precip ${cur.precipitation}`);
            if (this.statsEl) {
                this.statsEl.innerHTML = chips.map((c) => `<span class="weather-chip">${c}</span>`).join("");
            }
            // details (only really useful when expanded, but safe to compute always)
            if (this.detailsEl) {
                const daily = (_b = data.daily) !== null && _b !== void 0 ? _b : {};
                const day0Max = (_c = daily.temperature_2m_max) === null || _c === void 0 ? void 0 : _c[0];
                const day0Min = (_d = daily.temperature_2m_min) === null || _d === void 0 ? void 0 : _d[0];
                const day0Pop = (_e = daily.precipitation_probability_max) === null || _e === void 0 ? void 0 : _e[0];
                const day0Code = (_f = daily.weather_code) === null || _f === void 0 ? void 0 : _f[0];
                const d0 = weatherCodeToTextAndIcon(day0Code);
                const parts = [];
                if (typeof day0Max === "number" && typeof day0Min === "number") {
                    parts.push(`Today: ${Math.round(day0Min)}° – ${Math.round(day0Max)}°`);
                }
                if (typeof day0Pop === "number")
                    parts.push(`Precip chance max: ${Math.round(clamp(day0Pop, 0, 100))}%`);
                parts.push(`Outlook: ${d0.text} ${d0.icon}`);
                this.detailsEl.innerHTML = parts.map((p) => `<div>${p}</div>`).join("");
            }
            // updated text
            if (this.updatedEl) {
                const d = new Date();
                this.updatedEl.textContent = `Updated ${d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
            }
            // collapsed meta: show a “notification-like” one-liner
            const metaOneLine = typeof t === "number" ? `${icon} ${Math.round(t)}° • ${text}` : `${icon} ${text}`;
            this.setMeta(metaOneLine);
        }
        catch (e) {
            const msg = (e === null || e === void 0 ? void 0 : e.code) === 1
                ? "Location blocked — click Refresh to retry"
                : `Weather unavailable — ${String((_g = e === null || e === void 0 ? void 0 : e.message) !== null && _g !== void 0 ? _g : e)}`;
            this.setMeta(msg);
            if (this.detailsEl)
                this.detailsEl.textContent = "";
            if (this.statsEl)
                this.statsEl.innerHTML = "";
            if (this.locEl)
                this.locEl.textContent = "—";
            if (this.tempEl)
                this.tempEl.textContent = "—";
            if (this.descEl)
                this.descEl.textContent = "—";
            if (this.iconEl)
                this.iconEl.textContent = "❓";
        }
    }
}
//# sourceMappingURL=weather.js.map