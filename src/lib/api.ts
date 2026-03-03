import { type BPReading } from "./bp-utils";

const API_BASE = "http://localhost:8000/api";

export const getInsights = async (userProfile: any, dailyLogs: BPReading[]) => {
  const response = await fetch(`${API_BASE}/insights`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_profile: userProfile,
      daily_logs: dailyLogs,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to fetch insights");
  }

  return response.json();
};

export const saveHealthLog = async (logData: any) => {
  const response = await fetch(`${API_BASE}/history`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(logData),
  });

  if (!response.ok) {
    throw new Error("Failed to save health log");
  }

  return response.json();
};

export const getHistory = async (userId: string) => {
  const response = await fetch(`${API_BASE}/history/${userId}`);

  if (!response.ok) {
    throw new Error("Failed to fetch history");
  }

  return response.json();
};

export const getDailySummary = async (userId: string, date: string) => {
  const response = await fetch(`${API_BASE}/history/${userId}/${date}`);

  if (!response.ok) {
    throw new Error("Failed to fetch daily summary");
  }

  return response.json();
};
