export function formatUtcOffsetLabel(timeZone: string): string {
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
    const tzPart = parts.find((p) => p.type === "timeZoneName")?.value ?? "";
    // tzPart often "GMT+8" / "UTC+8" / "GMT-5"
    return tzPart.replace("GMT", "UTC");
  } catch {
    return "UTC";
  }
}

export type ReverseGeocodeResponse = {
  name?: string;
  admin1?: string;
  country?: string;
  country_code?: string;
  timezone?: string;
};

export function buildPlaceLabel(geo: ReverseGeocodeResponse | null, fallbackLat: number, fallbackLon: number): string {
  if (!geo) return `Lat ${fallbackLat.toFixed(2)}, Lon ${fallbackLon.toFixed(2)}`;
  const parts = [geo.name, geo.admin1, geo.country].filter(Boolean);
  return parts.length ? parts.join(", ") : `Lat ${fallbackLat.toFixed(2)}, Lon ${fallbackLon.toFixed(2)}`;
}


export type WeatherTexture =
  | "clear"
  | "cloudy"
    | "sandstorm"
  | "fog"
  | "drizzle"
  | "rain"
    | "heavy_rain"
  | "snow"
    | "heavy_snow"
  | "thunderstorm"
  | "mixed";

export function weatherCodeToTexture(code: number | undefined | null): WeatherTexture {
  if (code === undefined || code === null) return "mixed";
  if (code === 0) return "clear";
  if (code >= 1 && code <= 3) return "cloudy";
    if (code >= 30 && code <= 35) return "sandstorm";
  if (code === 45 || code === 48) return "fog";
    if (code >= 50 && code <= 59) return "drizzle";
    if (code >= 60 && code <= 69) return "rain";
    if (code >= 80 && code <= 84) return "heavy_rain";
    if (code >= 70 && code <= 79) return "snow";
    if (code >= 85 && code <= 86) return "heavy_snow";
    if (code >= 90) return "thunderstorm";
  return "mixed";
}

