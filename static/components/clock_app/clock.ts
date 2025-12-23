// static/components/clock_app/clock.ts

type Coords = { lat: number; lon: number };

const WORLD_CITIES = [
    {
        name: "London",
        tz: "Europe/London",
        lat: 51.5074,
        lon: -0.1278,
    },
    {
        name: "New York",
        tz: "America/New_York",
        lat: 40.7128,
        lon: -74.0060,
    },
    {
        name: "Tokyo",
        tz: "Asia/Tokyo",
        lat: 35.6762,
        lon: 139.6503,
    },
    {
        name: "Sydney",
        tz: "Australia/Sydney",
        lat: -33.8688,
        lon: 151.2093,
    },
    {
        name: "Paris",
        tz: "Europe/Paris",
        lat: 48.8566,
        lon: 2.3522,
    },
    {
        name: "Dubai",
        tz: "Asia/Dubai",
        lat: 25.2048,
        lon: 55.2708,
    },
    {
        name: "Shanghai",
        tz: "Asia/Shanghai",
        lat: 31.2304,
        lon: 121.4737,
    },
    {
        name: "Los Angeles",
        tz: "America/Los_Angeles",
        lat: 34.0522,
        lon: -118.2437,
    },
];

export class ClockGadget {
    private root: HTMLElement;

    // Collapsed Elements
    private mainTimeEl: HTMLElement | null;
    private mainLocEl: HTMLElement | null;
    private mainDateEl: HTMLElement | null;

    // Expanded Elements
    private heroTimeEl: HTMLElement | null;
    private heroDateEl: HTMLElement | null;
    private heroLocEl: HTMLElement | null;
    private gridEl: HTMLElement | null;

    private earthMapContainer: HTMLElement | null;
    private earthCanvas: HTMLCanvasElement | null;
    private earthCtx: CanvasRenderingContext2D | null;
    private earthMarker: HTMLElement | null;
    private citiesLayer: HTMLElement | null;

    private timer: number | null = null;
    private coords: Coords | null = null;

    constructor(root: HTMLElement) {
        this.root = root;

        // Select elements
        this.mainTimeEl = root.querySelector("#clock-display-main");
        this.mainLocEl = root.querySelector("#clock-loc-main");
        this.mainDateEl = root.querySelector("#clock-date-main");

        this.heroTimeEl = root.querySelector("#clock-hero-time");
        this.heroDateEl = root.querySelector("#clock-hero-date");
        this.heroLocEl = root.querySelector("#clock-hero-loc");
        this.gridEl = root.querySelector("#clock-world-grid");

        this.earthCanvas = root.querySelector("#clock-earth-canvas");
        this.earthMapContainer = root.querySelector("#earth-map-container");
        this.earthMarker = root.querySelector("#clock-earth-marker");
        this.citiesLayer = root.querySelector("#clock-city-layer");
        this.earthCtx = this.earthCanvas ? this.earthCanvas.getContext("2d") : null;

        this.tick();
        this.timer = window.setInterval(() => this.tick(), 1000);
        this.renderCityMarkers();
        // 2. Fetch Location
        void this.initLocation();
    }

    private tick() {
        const now = new Date();

        // Format: 14:05
        const timeShort = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
        // Format: 14:05:32
        const timeLong = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });

        // Format: Mon, Jan 01
        const dateStr = now.toLocaleDateString([], { weekday: 'short', month: 'short', day: '2-digit' });
        // Format: Monday, January 01, 2025
        const dateFull = now.toLocaleDateString([], { weekday: 'long', month: 'long', day: '2-digit' });

        // Update Collapsed
        if (this.mainTimeEl) this.mainTimeEl.textContent = timeShort;
        if (this.mainDateEl) this.mainDateEl.textContent = dateStr;

        // Update Expanded Hero
        if (this.heroTimeEl) this.heroTimeEl.textContent = timeLong;
        if (this.heroDateEl) this.heroDateEl.textContent = dateFull;

        // Update World Grid (if expanded)
if (this.root.classList.contains("gadget--expanded")) {
            this.renderWorldGrid(now);

            // 🌍 Update Map Shadow (every tick is overkill, but smooth)
            this.drawEarth(now);
        }
    }

    private renderWorldGrid(now: Date) {
        if (!this.gridEl) return;

        // Simple optimization: don't re-render DOM if it exists, just update text?
        // For simplicity, we just rebuild string. Browsers handle small DOM changes fast.

        const cards = WORLD_CITIES.map(city => {
            const timeStr = now.toLocaleTimeString([], {
                timeZone: city.tz,
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            });

            // Calculate offset roughly (e.g. +5h)
            // Ideally we'd compare hours, but that's complex with dates.
            // We'll just show the time for now.

            return `
                <div class="clock-city-card">
                    <div class="clock-city-name">${city.name}</div>
                    <div class="clock-city-time">${timeStr}</div>
                </div>
            `;
        });

        this.gridEl.innerHTML = cards.join("");
    }

    // ============================================================
    // 🌍 EARTH DAY/NIGHT LOGIC
    // ============================================================

    private drawEarth(now: Date) {
        if (!this.earthCanvas || !this.earthCtx) return;

        const width = this.earthCanvas.width;
        const height = this.earthCanvas.height;
        const ctx = this.earthCtx;

        // 1. Clear Canvas
        ctx.clearRect(0, 0, width, height);

        // 2. Calculate Sun Position
        // Sun Longitude: 12:00 UTC = 0°. Earth rotates 15° per hour.
        // We invert it because the sun moves East -> West relative to map.
        const utcHours = now.getUTCHours() + now.getUTCMinutes() / 60;
        const sunLon = (12 - utcHours) * 15;

        // Sun Declination (Approximate for seasons)
        // Ranges from +23.44 (Summer Solstice) to -23.44 (Winter Solstice)
        const startOfYear = new Date(now.getFullYear(), 0, 1);
        const dayOfYear = Math.floor((now.getTime() - startOfYear.getTime()) / 86400000);
        // Simplified declination formula
        const sunLat = -23.44 * Math.cos((2 * Math.PI / 365) * (dayOfYear + 10));

        // 3. Draw Night Shadow (The Terminator)
        ctx.fillStyle = "rgba(0, 0, 0, 0.55)"; // Semi-transparent black shadow
        ctx.beginPath();

        // We iterate across the map width (longitude -180 to 180)
        // and find the Y (latitude) where day meets night.
        for (let x = 0; x <= width; x += 2) {
            const lon = (x / width) * 360 - 180; // Map x to longitude

            // The "Terminator" formula
            // tan(lat) = -1 / (tan(declination) * cos(hour_angle))
            // hour_angle = lon - sunLon
            const delta = (lon - sunLon) * (Math.PI / 180);
            const k = -1 / (Math.tan(sunLat * (Math.PI / 180)) * Math.cos(delta));

            let latRad = Math.atan(k);

            // Map Latitude (-90 to 90) to Y (height to 0)
            // Note: Equirectangular projection implies linear Y.
            let latDeg = latRad * (180 / Math.PI);

            // Fix wrap-around artifacts near poles logic
            // If cos(delta) > 0, we are on the "night" side of the terminator curve logic
            // Actually, a simpler way for canvas is usually to just draw the "Day" curve and fill inverse,
            // but let's stick to drawing the Night polygon.

            let y = (height / 2) - (latDeg * (height / 180));

            if (x === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }

        // Close the path to fill the "Night" side
        // If it's Northern Summer (Sun Lat > 0), the North Pole is light, South is dark.
        // We need to decide whether to close the loop via the Top or Bottom of the canvas.
        if (sunLat > 0) {
            // Northern Summer: Shadow covers the bottom
            ctx.lineTo(width, height);
            ctx.lineTo(0, height);
        } else {
            // Northern Winter: Shadow covers the top
            ctx.lineTo(width, 0);
            ctx.lineTo(0, 0);
        }

        ctx.closePath();
        ctx.fill();

        // 4. Update "You Are Here" Marker
        if (this.earthMarker && this.coords) {
            this.earthMarker.style.display = "block";
            // Map Lat/Lon to %
            const xPct = ((this.coords.lon + 180) / 360) * 100;
            const yPct = ((90 - this.coords.lat) / 180) * 100;

            this.earthMarker.style.left = `${xPct}%`;
            this.earthMarker.style.top = `${yPct}%`;
        }
    }

    private renderCityMarkers() {
        if (!this.citiesLayer) return;

        const dots = WORLD_CITIES.map(city => {
            // 1. Calculate Positions (0-100%)
            // Map: -180 (Left) to +180 (Right)
            const xPct = ((city.lon + 180) / 360) * 100;

            // Map: +90 (Top) to -90 (Bottom)
            const yPct = ((90 - city.lat) / 180) * 100;

            // 2. Return the HTML string with inline styles
            // Note: We use 'title' so hovering shows the city name
            return `<div class="city-marker" 
                         style="left: ${xPct}%; top: ${yPct}%;" 
                         title="${city.name}">
                    </div>`;
        });

        // 3. Insert safely into the layer (preserving canvas)
        this.citiesLayer.innerHTML = dots.join("");
    }

    // ... initLocation, reverseGeocode, updateLocText ...
    private async initLocation() {
        // (Copy your previous logic here)
        try {
            const cached = localStorage.getItem("weather.coords");
            if (cached) {
                this.coords = JSON.parse(cached);
                void this.reverseGeocode();
                // 🌍 Trigger immediate redraw once we have coords
                this.drawEarth(new Date());
                return;
            }
        } catch {}

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    this.coords = { lat: pos.coords.latitude, lon: pos.coords.longitude };
                    void this.reverseGeocode();
                    this.drawEarth(new Date());
                },
                (err) => {
                    console.warn(err);
                    this.updateLocText("Location Unknown");
                }
            );
        }
    }

    private async reverseGeocode() {
        if (!this.coords) return;

        try {
            const params = new URLSearchParams({
                lat: String(this.coords.lat),
                lon: String(this.coords.lon)
            });

            const res = await fetch(`/api/reverse_geocode?${params.toString()}`);
            if (!res.ok) throw new Error("API Error");

            const data = await res.json();
            // Construct label: "New York, NY" or "Tokyo, Japan"
            const label = [data.name, data.admin1, data.country]
                .filter(Boolean)
                .slice(0, 2) // Keep it short
                .join(", ");

            this.updateLocText(label);

        } catch (e) {
            console.error(e);
            this.updateLocText("Unknown Place");
        }
    }

    private updateLocText(text: string) {
        if (this.mainLocEl) this.mainLocEl.textContent = text;
        if (this.heroLocEl) this.heroLocEl.textContent = text;
    }
}