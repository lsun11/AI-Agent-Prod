// static/components/stock_app/stock.ts

interface PricePoint {
    time: number;
    price: number;
    vol: number;
}

const RANGES: Record<string, { duration: number; points: number; interval: number }> = {
    "1H": { duration: 3600 * 1000, points: 60, interval: 60 * 1000 },
    "1D": { duration: 6.5 * 3600 * 1000, points: 78, interval: 5 * 60 * 1000 }, // Trading day
    "1W": { duration: 7 * 24 * 3600 * 1000, points: 168, interval: 3600 * 1000 },
    "1M": { duration: 30 * 24 * 3600 * 1000, points: 30, interval: 24 * 3600 * 1000 },
    "6M": { duration: 180 * 24 * 3600 * 1000, points: 180, interval: 24 * 3600 * 1000 },
    "1Y": { duration: 365 * 24 * 3600 * 1000, points: 250, interval: 24 * 3600 * 1000 },
    "5Y": { duration: 5 * 365 * 24 * 3600 * 1000, points: 260, interval: 7 * 24 * 3600 * 1000 }
};

class TickerData {
    symbol: string;
    currentPrice: number;
    history: PricePoint[];
    private volatility: number;
    private trend: number;

    constructor(symbol: string, startPrice: number, vol: number) {
        this.symbol = symbol;
        this.currentPrice = startPrice;
        this.volatility = vol;
        this.trend = (Math.random() - 0.5) * 0.1;
        this.history = [];
    }

    // Generate historical fake data
    generate(rangeKey: string) {
        const config = RANGES[rangeKey] || RANGES["1D"];
        this.history = [];
        let p = this.currentPrice;
        const now = Date.now();

        // Work backwards
        // @ts-ignore
        for (let i = config.points; i >= 0; i--) {
            p = p * (1 + (Math.random() - 0.5 + this.trend * 0.05) * (this.volatility * 0.05));
            // @ts-ignore
            const time = now - (i * config.interval);

            // ✅ FIX: Consistent Volume Scale (0.5M - 5M avg)
            const v = Math.floor(Math.random() * 4500000) + 500000;

            this.history.push({ time, price: p, vol: v });
        }
        // @ts-ignore
        this.currentPrice = this.history[this.history.length-1].price;
    }

    // Tick forward (Live Market Simulation)
    tick(rangeKey: string, isMarketOpen: boolean) {
        if (!isMarketOpen) return; // 🛑 Stop ticking if closed

        const changePct = (Math.random() - 0.5) * (this.volatility * 0.01);
        this.currentPrice = this.currentPrice * (1 + changePct);
        const now = Date.now();

        // ✅ FIX: Volume matches historical scale
        const newVol = Math.floor(Math.random() * 4500000) + 500000;

        // ✅ FIX: Smart Update Logic
        // If Intraday (1H, 1D): Scroll the chart (push new, remove old)
        if (rangeKey === "1H" || rangeKey === "1D") {
            this.history.push({ time: now, price: this.currentPrice, vol: newVol });
            this.history.shift();
        }
        // If Long Term (1W+): Update ONLY the last candle (don't scroll)
        else {
            const last = this.history[this.history.length - 1];
            // @ts-ignore
            last.price = this.currentPrice;
            // @ts-ignore
            last.time = now; // Update timestamp to "now"
            // Accumulate volume for the day/week instead of replacing
            // @ts-ignore
            last.vol += Math.floor(newVol / 100);
        }
    }
}

export class StockGadget {
    private root: HTMLElement;
    private canvas: HTMLCanvasElement | null;
    private ctx: CanvasRenderingContext2D | null;

    private heroPrice: HTMLElement | null;
    private heroChange: HTMLElement | null;
    private volEl: HTMLElement | null;
    private miniSpy: HTMLElement | null;
    private miniQqq: HTMLElement | null;

    private tickers: Record<string, TickerData> = {};
    private activeSymbol: string = "SPY";
    private activeRange: string = "1D";
    private timer: number | null = null;
    private marketOpen: boolean = false;

    constructor(root: HTMLElement) {
        this.root = root;
        this.checkMarketStatus(); // Initial Check

        this.tickers["SPY"] = new TickerData("SPY", 475.00, 0.2);
        this.tickers["QQQ"] = new TickerData("QQQ", 408.00, 0.3);

        this.tickers["SPY"].generate(this.activeRange);
        this.tickers["QQQ"].generate(this.activeRange);

        this.canvas = root.querySelector("#stock-canvas");
        this.ctx = this.canvas ? this.canvas.getContext("2d") : null;
        this.heroPrice = root.querySelector("#stock-hero-price");
        this.heroChange = root.querySelector("#stock-hero-change");
        this.volEl = root.querySelector("#stock-hero-vol");

        this.miniSpy = root.querySelector("#stock-mini-spy");
        this.miniQqq = root.querySelector("#stock-mini-qqq");

        // Force initial paint of mini tickers
        if (this.miniSpy) this.renderMini(this.miniSpy, this.tickers["SPY"]);
        if (this.miniQqq) this.renderMini(this.miniQqq, this.tickers["QQQ"]);

        // Tabs
        const tabs = root.querySelectorAll(".stock-tab");
        tabs.forEach(btn => {
            btn.addEventListener("click", () => {
                tabs.forEach(t => t.classList.remove("active"));
                btn.classList.add("active");
                const sym = btn.getAttribute("data-symbol");
                if (sym) {
                    this.activeSymbol = sym;
                    this.drawChart();
                    this.updateUI();
                }
            });
        });

        // Ranges
        const rangeBtns = root.querySelectorAll(".stock-range-btn");
        rangeBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                rangeBtns.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                const rng = btn.getAttribute("data-range");
                if (rng) {
                    this.activeRange = rng;
                    Object.values(this.tickers).forEach(t => t.generate(this.activeRange));
                    this.drawChart();
                }
            });
        });

        const observer = new ResizeObserver(() => this.resizeCanvas());
        if (this.canvas) observer.observe(this.canvas);

        this.timer = window.setInterval(() => this.update(), 1000);
        requestAnimationFrame(() => this.resizeCanvas());
    }

    private checkMarketStatus() {
        const now = new Date();
        const day = now.getDay(); // 0 = Sun, 6 = Sat
        const hour = now.getHours();
        const min = now.getMinutes();

        // Simple US Market Rules (9:30 - 16:00 ET approx)
        // Adjust logic for your local timezone simulation or exact requirements
        const isWeekend = (day === 0 || day === 6);
        const isTradingHours = (hour > 9 || (hour === 9 && min >= 30)) && hour < 16;

        // Hardcoded Christmas Check for your specific context
        const isChristmas = (now.getMonth() === 11 && now.getDate() === 25);

        if (isWeekend || isChristmas || !isTradingHours) {
            this.marketOpen = false;
        } else {
            this.marketOpen = true;
        }
    }

    private update() {
        // @ts-ignore
        this.tickers[this.activeSymbol].tick(this.activeRange, this.marketOpen);
        this.updateUI();

        // Only redraw chart if market is open OR data changed
        // For UI responsiveness, we usually just draw.
        this.drawChart();
    }

    private updateUI() {
        if (this.miniSpy) { // @ts-ignore
            this.renderMini(this.miniSpy, this.tickers["SPY"]);
        }
        if (this.miniQqq) { // @ts-ignore
            this.renderMini(this.miniQqq, this.tickers["QQQ"]);
        }

        const data = this.tickers[this.activeSymbol];
        if (!data) return;

        if (this.heroPrice) this.heroPrice.textContent = data.currentPrice.toFixed(2);

        // @ts-ignore
        const startPrice = data.history[0].price;
        const diff = data.currentPrice - startPrice;
        const pct = (diff / startPrice) * 100;
        const sign = diff >= 0 ? "+" : "";

        if (this.heroChange) {
            // ✅ Display "CLOSED" if market is closed
            if (!this.marketOpen) {
                this.heroChange.textContent = `MARKET CLOSED • ${sign}${diff.toFixed(2)} (${pct.toFixed(2)}%)`;
                this.heroChange.className = "stock-hero-change";
                this.heroChange.style.color = "#8892b0"; // Grey
            } else {
                this.heroChange.textContent = `${sign}${diff.toFixed(2)} (${sign}${pct.toFixed(2)}%)`;
                this.heroChange.className = "stock-hero-change " + (diff >= 0 ? "green" : "red");
                this.heroChange.style.color = ""; // Reset
            }
        }

        const totalVol = data.history.reduce((acc, p) => acc + p.vol, 0);
        if (this.volEl) {
             this.volEl.textContent = this.formatBigNumber(totalVol);
        }
    }

    private renderMini(el: HTMLElement, data: TickerData) {
        el.textContent = data.currentPrice.toFixed(2);
        // @ts-ignore
        const startPrice = data.history.length > 0 ? data.history[0].price : data.currentPrice;
        const isUp = data.currentPrice >= startPrice;
        el.className = `stock-mini-price ${isUp ? 'up' : 'down'}`;
    }

    private resizeCanvas() {
        if (!this.canvas) return;
        const rect = this.canvas.parentElement?.getBoundingClientRect();
        if (rect && rect.width > 0 && rect.height > 0) {
            this.canvas.width = rect.width;
            this.canvas.height = rect.height;
            this.drawChart();
        }
    }

    // =========================================================================
    // 📊 CHART ENGINE (Unchanged from previous valid version)
    // =========================================================================
    // ... [Copy the drawChart, drawXAxis, helpers, and Math functions from previous step] ...
    // ... [They are perfectly compatible with this new logic] ...

    // (I am including the drawChart block again below for safety/Copy-Paste convenience)

    private drawChart() {
        if (!this.ctx || !this.canvas) return;
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;
        const data = this.tickers[this.activeSymbol];

        if (!data || h === 0) return;

        ctx.clearRect(0, 0, w, h);
        if (data.history.length < 5) return;

        const xAxisH = 20;
        const chartH = h - xAxisH;
        const pad = 4;
        const hPrice = chartH * 0.50;
        const hVol   = chartH * 0.15;
        const hMACD  = chartH * 0.175;
        const hRSI   = chartH * 0.175;
        const yPrice = 0;
        const yVol   = hPrice + pad;
        const yMACD  = yVol + hVol + pad;
        const yRSI   = yMACD + hMACD + pad;
        const yXAxis = h - xAxisH;

        const prices = data.history.map(p => p.price);
        const volumes = data.history.map(p => p.vol);
        const times = data.history.map(p => p.time);

        // 1. PRICE
        this.drawPaneBackground(ctx, yPrice, hPrice, w, "rgba(255,255,255,0.02)");
        this.drawGrid(ctx, yPrice, hPrice, w, 6, 4);
        const minP = this.safeMin(prices);
        const maxP = this.safeMax(prices);
        const smaValues = this.calculateSMA(prices, 20);
        this.drawPaneFixed(ctx, smaValues, yPrice, hPrice, w, "#f1c40f", minP, maxP);
        const emaValues = this.calculateEMA(prices, 20);
        this.drawPaneFixed(ctx, emaValues, yPrice, hPrice, w, "#e67e22", minP, maxP);
        this.drawPaneFixed(ctx, prices, yPrice, hPrice, w, "#45a29e", minP, maxP);
        this.drawLabel(ctx, "PRICE / SMA(20) / EMA(20)", yPrice);
        this.drawYAxis(ctx, prices, yPrice, hPrice, w, 2, "$");

        // 2. VOLUME
        this.drawPaneBackground(ctx, yVol, hVol, w, "rgba(255,255,255,0.02)");
        this.drawVolumePane(ctx, volumes, yVol, hVol, w);
        this.drawLabel(ctx, "VOL", yVol);
        this.drawYAxis(ctx, volumes, yVol, hVol, w, 0, "", true);

        // 3. MACD
        this.drawPaneBackground(ctx, yMACD, hMACD, w, "rgba(255,255,255,0.02)");
        const macdValues = this.calculateMACDArray(prices);
        const minM = this.safeMin(macdValues);
        const maxM = this.safeMax(macdValues);
        const rangeM = maxM - minM || 1;
        const zeroY = yMACD + hMACD - ((0 - minM) / rangeM * hMACD);
        ctx.beginPath(); ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
        ctx.moveTo(0, zeroY); ctx.lineTo(w, zeroY); ctx.stroke();
        this.drawPane(ctx, macdValues, yMACD, hMACD, w, "#00ffcc", false);
        this.drawLabel(ctx, "MACD", yMACD);
        this.drawYAxis(ctx, macdValues, yMACD, hMACD, w, 2, "");

        // 4. RSI
        this.drawPaneBackground(ctx, yRSI, hRSI, w, "rgba(255,255,255,0.02)");
        const rsiValues = this.calculateRSIArray(prices, 14);
        const top70 = yRSI + hRSI * 0.3;
        const bot30 = yRSI + hRSI * 0.7;
        ctx.beginPath(); ctx.strokeStyle = "rgba(255, 255, 255, 0.1)"; ctx.setLineDash([2, 2]);
        ctx.moveTo(0, top70); ctx.lineTo(w, top70); ctx.moveTo(0, bot30); ctx.lineTo(w, bot30);
        ctx.stroke(); ctx.setLineDash([]);
        this.drawPaneFixed(ctx, rsiValues, yRSI, hRSI, w, "#ff00ff", 0, 100);
        this.drawLabel(ctx, "RSI", yRSI);
        this.drawYAxisFixed(ctx, 0, 100, yRSI, hRSI, w);

        // 5. X-AXIS
        this.drawXAxis(ctx, times, yXAxis, xAxisH, w);
    }

    // --- COPY THE HELPERS FROM PREVIOUS STEP BELOW ---
    // (drawXAxis, drawGrid, safeMin, safeMax, drawPane, drawPaneFixed, drawYAxis, etc.)
    private drawXAxis(ctx: CanvasRenderingContext2D, times: number[], y: number, h: number, w: number) {
        ctx.save(); ctx.fillStyle = "#556080"; ctx.font = "9px 'Roboto Mono', monospace"; ctx.textAlign = "center";
        const isIntraday = ["1H", "1D"].includes(this.activeRange);
        const count = 5;
        for (let i = 0; i < count; i++) {
            const idx = Math.floor((times.length - 1) * (i / (count - 1)));
            const time = times[idx];
            if (!time) continue;
            const date = new Date(time);
            let text = "";
            if (isIntraday) text = date.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute:'2-digit' });
            else if (this.activeRange === "1W" || this.activeRange === "1M") text = date.toLocaleDateString([], { month: 'short', day: 'numeric' });
            else text = date.toLocaleDateString([], { month: 'short', year: '2-digit' });
            const x = (idx / (times.length - 1)) * w;
            if (i === 0) ctx.textAlign = "left"; else if (i === count - 1) ctx.textAlign = "right"; else ctx.textAlign = "center";
            ctx.fillText(text, x, y + 14);
        }
        ctx.restore();
    }
    private drawGrid(ctx: CanvasRenderingContext2D, topY: number, h: number, w: number, vLines: number, hLines: number) {
        ctx.save(); ctx.strokeStyle = "rgba(255, 255, 255, 0.05)"; ctx.lineWidth = 1; ctx.beginPath();
        const stepX = w / vLines; for(let i=1; i<vLines; i++) { const x = i * stepX; ctx.moveTo(x, topY); ctx.lineTo(x, topY + h); }
        const stepY = h / hLines; for(let i=1; i<hLines; i++) { const y = topY + (i * stepY); ctx.moveTo(0, y); ctx.lineTo(w, y); }
        ctx.stroke(); ctx.restore();
    }
    private safeMin(values: number[]): number { let m = Infinity; for(let v of values) { if(Number.isFinite(v) && v < m) m = v; } return m === Infinity ? 0 : m; }
    private safeMax(values: number[]): number { let m = -Infinity; for(let v of values) { if(Number.isFinite(v) && v > m) m = v; } return m === -Infinity ? 0 : m; }
    private drawPaneBackground(ctx: CanvasRenderingContext2D, y: number, h: number, w: number, color: string) { ctx.fillStyle = color; ctx.fillRect(0, y, w, h); }
    private drawLabel(ctx: CanvasRenderingContext2D, text: string, y: number) { ctx.save(); ctx.fillStyle = "#556080"; ctx.font = "bold 10px sans-serif"; ctx.fillText(text, 4, y + 10); ctx.restore(); }
    private drawYAxis(ctx: CanvasRenderingContext2D, values: number[], topY: number, h: number, w: number, decimals: number, prefix: string, compact: boolean = false) {
        if (values.length === 0) return; const min = this.safeMin(values); const max = this.safeMax(values); const mid = (min + max) / 2;
        ctx.save(); ctx.fillStyle = "rgba(255, 255, 255, 0.5)"; ctx.font = "9px 'Roboto Mono', monospace"; ctx.textAlign = "right"; ctx.textBaseline = "middle";
        const fmt = (val: number) => compact ? this.formatBigNumber(val) : prefix + val.toFixed(decimals);
        ctx.fillText(fmt(max), w - 4, topY + 10); ctx.fillText(fmt(mid), w - 4, topY + (h / 2)); ctx.fillText(fmt(min), w - 4, topY + h - 6); ctx.restore();
    }
    private drawYAxisFixed(ctx: CanvasRenderingContext2D, min: number, max: number, topY: number, h: number, w: number) {
        ctx.save(); ctx.fillStyle = "rgba(255, 255, 255, 0.5)"; ctx.font = "9px 'Roboto Mono', monospace"; ctx.textAlign = "right"; ctx.textBaseline = "middle";
        ctx.fillText(max.toString(), w - 4, topY + 10); ctx.fillText("50", w - 4, topY + (h / 2)); ctx.fillText(min.toString(), w - 4, topY + h - 6); ctx.restore();
    }
    private formatBigNumber(num: number): string { if (num >= 1000000) return (num / 1000000).toFixed(1) + "M"; if (num >= 1000) return (num / 1000).toFixed(0) + "K"; return num.toFixed(0); }
    private drawVolumePane(ctx: CanvasRenderingContext2D, volumes: number[], topY: number, h: number, w: number) {
        if (volumes.length === 0) return; const maxV = this.safeMax(volumes) || 1; const stepX = w / (volumes.length - 1); const barW = Math.max(1, stepX - 1);
        ctx.save(); ctx.fillStyle = "#45a29e";
        volumes.forEach((v, i) => { if (!Number.isFinite(v)) return; const x = i * stepX; const vHeight = (v / maxV) * h; const y = topY + h - vHeight; ctx.fillRect(x, y, barW, vHeight); }); ctx.restore();
    }
    private drawPane(ctx: CanvasRenderingContext2D, values: number[], topY: number, h: number, w: number, color: string, fill: boolean) {
        if (values.length === 0) return; const min = this.safeMin(values); const max = this.safeMax(values); const range = max - min || 1; const stepX = w / (values.length - 1);
        ctx.save(); ctx.beginPath(); ctx.strokeStyle = color; ctx.lineWidth = 1.5; let firstPoint = true;
        values.forEach((val, i) => { if (!Number.isFinite(val)) return; const x = i * stepX; const normalizedY = (val - min) / range; const y = topY + h - (normalizedY * h); if (firstPoint) { ctx.moveTo(x, y); firstPoint = false; } else ctx.lineTo(x, y); });
        ctx.stroke(); if (fill) { ctx.lineTo(w, topY + h); ctx.lineTo(0, topY + h); ctx.closePath(); const grad = ctx.createLinearGradient(0, topY, 0, topY + h); const baseColor = color.startsWith("#") ? this.hexToRgb(color) : "100,255,255"; grad.addColorStop(0, `rgba(${baseColor}, 0.2)`); grad.addColorStop(1, `rgba(${baseColor}, 0)`); ctx.fillStyle = grad; ctx.fill(); } ctx.restore();
    }
    private drawPaneFixed(ctx: CanvasRenderingContext2D, values: number[], topY: number, h: number, w: number, color: string, min: number, max: number) {
        if (values.length === 0) return; const range = max - min; const stepX = w / (values.length - 1);
        ctx.save(); ctx.beginPath(); ctx.strokeStyle = color; ctx.lineWidth = 1.5; let firstPoint = true;
        values.forEach((val, i) => { if (!Number.isFinite(val)) return; const x = i * stepX; const normalizedY = (val - min) / range; const y = topY + h - (normalizedY * h); if (firstPoint) { ctx.moveTo(x, y); firstPoint = false; } else ctx.lineTo(x, y); }); ctx.stroke(); ctx.restore();
    }
    private hexToRgb(hex: string): string { const bigint = parseInt(hex.slice(1), 16); const r = (bigint >> 16) & 255; const g = (bigint >> 8) & 255; const b = bigint & 255; return `${r},${g},${b}`; }
    private calculateSMA(prices: number[], window: number): number[] { const result: number[] = []; for (let i = 0; i < prices.length; i++) { if (i < window - 1) { result.push(NaN); } else { let sum = 0; for (let j = 0; j < window; j++) { // @ts-ignore
        sum += prices[i - j];
    } result.push(sum / window); } } return result; }
    private calculateEMA(prices: number[], window: number): number[] { const result: number[] = []; const k = 2 / (window + 1); let sum = 0; for(let i=0; i<window; i++) sum += prices[i] || 0; let ema = sum / window; for (let i = 0; i < prices.length; i++) { if (i < window) { result.push(NaN); } else { const price = prices[i]; // @ts-ignore
        ema = (price * k) + (ema * (1 - k)); result.push(ema); } } return result; }
    private calculateRSIArray(prices: number[], period: number = 14): number[] { const rsiArr: number[] = []; let gains = 0; let losses = 0; for (let i = 1; i < prices.length; i++) { const pNow = prices[i] ?? 0; const pPrev = prices[i-1] ?? 0; const change = pNow - pPrev; if (i <= period) { if (change > 0) gains += change; else losses -= change; if (i === period) { let rs = losses === 0 ? 100 : (gains / period) / (losses / period); rsiArr.push(100 - (100 / (1 + rs))); } else rsiArr.push(50); } else { let winG = 0; let winL = 0; for (let j = i - period + 1; j <= i; j++) { const pj = prices[j] ?? 0; const pjPrev = prices[j-1] ?? 0; const ch = pj - pjPrev; if (ch > 0) winG += ch; else winL -= ch; } const rs = winL === 0 ? 100 : winG / winL; rsiArr.push(100 - (100 / (1 + rs))); } } while(rsiArr.length < prices.length) rsiArr.unshift(50); return rsiArr; }
    private calculateMACDArray(prices: number[]): number[] { const macd: number[] = []; const ema12 = this.movingAverage(prices, 12); const ema26 = this.movingAverage(prices, 26); for (let i = 0; i < prices.length; i++) { macd.push((ema12[i] ?? 0) - (ema26[i] ?? 0)); } return macd; }
    private movingAverage(data: number[], window: number): number[] { const result: number[] = []; for (let i = 0; i < data.length; i++) { if (i < window) result.push(data[i] ?? 0); else { let sum = 0; for (let j = 0; j < window; j++) sum += data[i-j] ?? 0; result.push(sum / window); } } return result; }
}