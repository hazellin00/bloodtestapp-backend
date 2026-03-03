// Blood pressure classification utilities

export type BPLevel = "normal" | "elevated" | "high1" | "high2" | "crisis";

export interface BPReading {
  systolic: number;
  diastolic: number;
  heartRate?: number;
  timestamp: string;
  period: "morning" | "evening";
  sessionIndex: number; // 1 or 2 within a period
}

export interface DayRecord {
  day: number; // 1-7
  morning: BPReading[];
  evening: BPReading[];
}

export function classifyBP(systolic: number, diastolic: number): BPLevel {
  if (systolic >= 180 || diastolic >= 120) return "crisis";
  if (systolic >= 140 || diastolic >= 90) return "high2";
  if (systolic >= 130 || diastolic >= 80) return "high1";
  if (systolic >= 120 && diastolic < 80) return "elevated";
  return "normal";
}

export function getBPColor(level: BPLevel): string {
  switch (level) {
    case "normal": return "bp-green";
    case "elevated": return "bp-yellow";
    case "high1": return "bp-orange";
    case "high2": return "bp-red";
    case "crisis": return "bp-red";
  }
}

export function getBPLabel(level: BPLevel): string {
  switch (level) {
    case "normal": return "正常";
    case "elevated": return "偏高";
    case "high1": return "高血壓第一期";
    case "high2": return "高血壓第二期";
    case "crisis": return "高血壓危象";
  }
}

export function averageReadings(readings: BPReading[]): { systolic: number; diastolic: number; heartRate: number } | null {
  if (readings.length === 0) return null;
  const avg = {
    systolic: Math.round(readings.reduce((s, r) => s + r.systolic, 0) / readings.length),
    diastolic: Math.round(readings.reduce((s, r) => s + r.diastolic, 0) / readings.length),
    heartRate: Math.round(readings.reduce((s, r) => s + (r.heartRate || 0), 0) / readings.length),
  };
  return avg;
}

export const MEDICAL_DISCLAIMER = "僅供參考；調整任何藥物前請諮詢您的醫師。";
