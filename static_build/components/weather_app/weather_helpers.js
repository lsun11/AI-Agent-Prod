export function formatUtcOffsetLabel(timeZone) {
    var _a, _b;
    // Use Intl to compute offset reliably
    try {
        const now = new Date();
        const dtf = new Intl.DateTimeFormat("en-US", {
            timeZone,
            hour: "2-digit",
            minute: "2-digit",
            timeZoneName: "shortOffset", // e.g. GMT+8 in modern browsers
        });
        const parts = dtf.formatToParts(now);
        const tzPart = (_b = (_a = parts.find((p) => p.type === "timeZoneName")) === null || _a === void 0 ? void 0 : _a.value) !== null && _b !== void 0 ? _b : "";
        // tzPart often "GMT+8" / "UTC+8" / "GMT-5"
        return tzPart.replace("GMT", "UTC");
    }
    catch (_c) {
        return "UTC";
    }
}
export function buildPlaceLabel(geo, fallbackLat, fallbackLon) {
    if (!geo)
        return `Lat ${fallbackLat.toFixed(2)}, Lon ${fallbackLon.toFixed(2)}`;
    const parts = [geo.name, geo.admin1, geo.country].filter(Boolean);
    return parts.length ? parts.join(", ") : `Lat ${fallbackLat.toFixed(2)}, Lon ${fallbackLon.toFixed(2)}`;
}
export function weatherCodeToTexture(code) {
    if (code === undefined || code === null)
        return "mixed";
    if (code === 0)
        return "clear";
    if (code >= 1 && code <= 3)
        return "cloudy";
    if (code === 45 || code === 48)
        return "fog";
    if (code >= 51 && code <= 57)
        return "drizzle";
    if (code >= 61 && code <= 67)
        return "rain";
    if (code >= 80 && code <= 82)
        return "rain";
    if (code >= 71 && code <= 77)
        return "snow";
    if (code >= 95)
        return "thunderstorm";
    return "mixed";
}
//# sourceMappingURL=weather_helpers.js.map