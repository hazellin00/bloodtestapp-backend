import { useState, useEffect } from "react";
import { format } from "date-fns";
import { Calendar } from "@/components/ui/calendar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Heart, CalendarDays, Loader2 } from "lucide-react";
import { getDailySummary } from "@/lib/api";
import type { BPReading } from "@/lib/bp-utils";

interface DaySummary {
  date: string;
  logs: any[];
  summary: string;
}

const CalendarHistory = () => {
  const [date, setDate] = useState<Date | undefined>(new Date());
  const [daySummary, setDaySummary] = useState<DaySummary | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!date) return;
    
    const fetchSummary = async () => {
      setIsLoading(true);
      setError(null);
      const selectedDateKey = format(date, "yyyy-MM-dd");
      
      try {
        // Assuming "dad-001" for now as per DadPortal.tsx fallback
        // Ideally this would come from an auth context or global state
        const data = await getDailySummary("dad-001", selectedDateKey);
        setDaySummary(data);
      } catch (err: any) {
        console.error("Failed to fetch summary:", err);
        setError("無法取得歷史紀錄，請稍後再試=(");
      } finally {
        setIsLoading(false);
      }
    };

    fetchSummary();
  }, [date]);

  const dayLogs = daySummary?.logs || [];

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <header className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-slate-900 flex items-center justify-center gap-3">
            <CalendarDays className="h-10 w-10 text-blue-600" />
            血壓歷史紀錄 (Blood Pressure History)
          </h1>
          <p className="text-xl text-slate-600">點擊日曆查看過去的測量結果</p>
        </header>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Calendar Section */}
          <Card className="shadow-lg border-0">
            <CardHeader className="bg-blue-50/50 pb-4">
              <CardTitle className="text-2xl text-blue-900">選擇日期</CardTitle>
            </CardHeader>
            <CardContent className="p-6 flex justify-center">
              <Calendar
                mode="single"
                selected={date}
                onSelect={setDate}
                className="rounded-md border shadow-sm p-4 w-full"
                classNames={{
                  day: "h-14 w-14 text-xl p-0 font-normal aria-selected:opacity-100",
                  head_cell: "text-lg font-medium text-slate-500 w-14",
                  caption_label: "text-2xl font-bold",
                  nav_button: "h-10 w-10",
                }}
              />
            </CardContent>
          </Card>

          {/* Results Section */}
          <div className="space-y-6">
            <h2 className="text-3xl font-semibold text-slate-800 border-b pb-2">
              {date ? format(date, "yyyy 年 MM 月 dd 日") : "請選擇日期"}
            </h2>

            {isLoading ? (
              <Card className="bg-slate-50 border-dashed border-2">
                <CardContent className="flex flex-col items-center justify-center h-48 text-slate-500">
                  <Loader2 className="h-12 w-12 mb-4 animate-spin text-primary" />
                  <p className="text-xl">正在載入紀錄中...</p>
                </CardContent>
              </Card>
            ) : error ? (
              <Card className="bg-red-50 border-red-200">
                <CardContent className="flex flex-col items-center justify-center h-48 text-red-500">
                  <Activity className="h-12 w-12 mb-4" />
                  <p className="text-xl font-bold">{error}</p>
                </CardContent>
              </Card>
            ) : dayLogs.length === 0 ? (
              <Card className="bg-slate-50 border-dashed border-2">
                <CardContent className="flex flex-col items-center justify-center h-48 text-slate-500">
                  <Activity className="h-12 w-12 mb-4 opacity-50" />
                  <p className="text-xl">這天沒有測量紀錄</p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {/* AI Summary Block */}
                {daySummary?.summary && (
                  <Card className="bg-blue-50 border-blue-200 shadow-sm">
                    <CardContent className="p-4">
                      <p className="elder-text text-blue-900 leading-relaxed font-medium">✨ {daySummary.summary}</p>
                    </CardContent>
                  </Card>
                )}

                {dayLogs.map((log, index) => {
                  const isNormal = log.systolic < 120 && log.diastolic < 80;
                  const isWarning = (log.systolic >= 120 && log.systolic <= 139) || (log.diastolic >= 80 && log.diastolic <= 89);
                  
                  let statusColor = "bg-red-50 border-red-200";
                  let textColor = "text-red-700";
                  
                  if (isNormal) {
                    statusColor = "bg-emerald-50 border-emerald-200";
                    textColor = "text-emerald-700";
                  } else if (isWarning) {
                    statusColor = "bg-amber-50 border-amber-200";
                    textColor = "text-amber-700";
                  }

                  return (
                    <Card key={index} className={`border-2 ${statusColor} transition-all hover:shadow-md`}>
                      <CardHeader className="pb-2">
                        <CardTitle className={`text-2xl flex items-center justify-between ${textColor}`}>
                          <span>{log.period === "morning" ? "🌅 早晨測量" : "🌃 晚間測量"}</span>
                          <Heart className="h-6 w-6" />
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-2 gap-4 text-center mt-2">
                          <div className="bg-white/60 p-4 rounded-xl">
                            <p className="text-sm text-slate-500 mb-1 font-medium">收縮壓 / 舒張壓</p>
                            <p className={`text-4xl font-bold ${textColor}`}>
                              {log.systolic} <span className="text-2xl text-slate-400">/</span> {log.diastolic}
                            </p>
                          </div>
                          <div className="bg-white/60 p-4 rounded-xl">
                            <p className="text-sm text-slate-500 mb-1 font-medium">心跳 (BPM)</p>
                            <p className="text-4xl font-bold text-slate-700">{log.heart_rate}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CalendarHistory;
