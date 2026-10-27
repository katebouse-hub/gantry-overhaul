export type ZoneColor = "red" | "blue" | "orange" | "yellow" | "black";

type ZoneSection = {
  id: string;
  x_min: number;
  x_max: number;
  y_min: number;
  y_max: number;
};

const ZONES: Record<ZoneColor, ZoneSection[]> = {
  red: [
    { id: "R1", x_min: 1, x_max: 3, y_min: 1, y_max: 5 },
    { id: "R2", x_min: 1, x_max: 3, y_min: 6, y_max: 10 },
    { id: "R3", x_min: 1, x_max: 3, y_min: 11, y_max: 15 },
    { id: "R4", x_min: 1, x_max: 3, y_min: 16, y_max: 20 },
  ],
  blue: [
    { id: "S01", x_min: 4, x_max: 8, y_min: 1, y_max: 5 },
    { id: "S02", x_min: 4, x_max: 8, y_min: 6, y_max: 10 },
    { id: "S03", x_min: 4, x_max: 8, y_min: 11, y_max: 15 },
    { id: "S04", x_min: 4, x_max: 8, y_min: 16, y_max: 20 },
    { id: "S05", x_min: 9, x_max: 13, y_min: 1, y_max: 5 },
  ],
  orange: [
    { id: "S06", x_min: 9, x_max: 13, y_min: 6, y_max: 10 },
    { id: "S07", x_min: 9, x_max: 13, y_min: 11, y_max: 15 },
    { id: "S08", x_min: 9, x_max: 13, y_min: 16, y_max: 20 },
    { id: "S10", x_min: 14, x_max: 18, y_min: 6, y_max: 10 },
    { id: "S12", x_min: 14, x_max: 18, y_min: 16, y_max: 20 },
  ],
  yellow: [
    { id: "S09", x_min: 14, x_max: 18, y_min: 1, y_max: 5 },
    { id: "S13", x_min: 19, x_max: 23, y_min: 1, y_max: 5 },
    { id: "S14", x_min: 19, x_max: 23, y_min: 6, y_max: 10 },
    { id: "S17", x_min: 24, x_max: 27, y_min: 1, y_max: 5 },
    { id: "S18", x_min: 24, x_max: 27, y_min: 6, y_max: 10 },
  ],
  black: [
    { id: "S11", x_min: 14, x_max: 18, y_min: 11, y_max: 15 },
    { id: "S15", x_min: 19, x_max: 23, y_min: 11, y_max: 15 },
    { id: "S16", x_min: 19, x_max: 23, y_min: 16, y_max: 20 },
    { id: "S19", x_min: 24, x_max: 27, y_min: 11, y_max: 15 },
    { id: "S20", x_min: 24, x_max: 27, y_min: 16, y_max: 20 },
  ],
};

export function getCellZone(x: number, y: number): ZoneColor | null {
  for (const [color, sections] of Object.entries(ZONES) as [ZoneColor, ZoneSection[]][]) {
    for (const s of sections) {
      if (x >= s.x_min && x <= s.x_max && y >= s.y_min && y <= s.y_max) {
        return color;
      }
    }
  }
  return null;
}

export function getCellSection(x: number, y: number): string | null {
  for (const sections of Object.values(ZONES)) {
    for (const s of sections) {
      if (x >= s.x_min && x <= s.x_max && y >= s.y_min && y <= s.y_max) {
        return s.id;
      }
    }
  }
  return null;
}

// Muted zone backgrounds for grid cells
export const ZONE_BG: Record<ZoneColor, string> = {
  red: "#fee2e2",
  blue: "#dbeafe",
  orange: "#ffedd5",
  yellow: "#fef9c3",
  black: "#e5e7eb",
};

// Vivid container colors
export const CONTAINER_STYLE: Record<string, { bg: string; text: string }> = {
  black: { bg: "#1f2937", text: "#ffffff" },
  yellow: { bg: "#f59e0b", text: "#000000" },
  orange: { bg: "#f97316", text: "#ffffff" },
  red: { bg: "#ef4444", text: "#ffffff" },
  blue: { bg: "#3b82f6", text: "#ffffff" },
};

export type GantryPos = { x: number; y: number; z: number };

export type Container = {
  id: string;
  color: string;
  pos_1: GantryPos;
  pos_2: GantryPos;
};

export type GantryState = { containers: Container[]; notes?: string };
