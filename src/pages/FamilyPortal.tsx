import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import MedicalDisclaimer from "@/components/MedicalDisclaimer";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { Users, TrendingUp, AlertTriangle, Link } from "lucide-react";

// Demo data for the chart
const demoData = [
  { day: "第1天", systolic: 132, diastolic: 85 },
  { day: "第2天", systolic: 128, diastolic: 82 },
  { day: "第3天", systolic: 135, diastolic: 88 },
  { day: "第4天", systolic: 125, diastolic: 80 },
  { day: "第5天", systolic: 142, diastolic: 92 },
  { day: "第6天", systolic: 130, diastolic: 84 },
  { day: "第7天", systolic: 126, diastolic: 79 },
];

const FamilyPortal = () => {
  const [familyCode, setFamilyCode] = useState("");
  const [isBound, setIsBound] = useState(false);

  const handleBind = () => {
    if (familyCode.trim().length >= 4) {
      setIsBound(true);
    }
  };

  const abnormalDays = demoData.filter((d) => d.systolic >= 140 || d.diastolic >= 90);

  return (
    <div className="min-h-screen bg-background p-4 md:p-8 max-w-4xl mx-auto">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Users className="w-8 h-8 text-primary" />
          <h1 className="text-3xl font-bold">家人健康儀表板</h1>
        </div>
        <p className="text-lg text-muted-foreground">隨時掌握家人的血壓狀況</p>
      </motion.div>

      {!isBound ? (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <Card className="max-w-md mx-auto">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-xl">
                <Link className="w-6 h-6" />
                綁定家人帳號
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">請輸入家人分享的家庭代碼來連結帳號</p>
              <Input
                placeholder="輸入家庭代碼"
                value={familyCode}
                onChange={(e) => setFamilyCode(e.target.value)}
                className="text-lg h-14"
              />
              <Button onClick={handleBind} disabled={familyCode.trim().length < 4} className="w-full h-14 text-lg font-bold">
                🔗 綁定帳號
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      ) : (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
          {/* Abnormality Alert */}
          {abnormalDays.length > 0 && (
            <motion.div
              initial={{ x: -20 }}
              animate={{ x: 0 }}
              className="bg-destructive/10 border border-destructive/30 rounded-2xl p-4 flex items-start gap-3"
            >
              <AlertTriangle className="w-6 h-6 text-destructive flex-shrink-0 mt-1" />
              <div>
                <p className="font-bold text-destructive text-lg">⚠️ 異常提醒</p>
                <p className="text-foreground">
                  過去7天中有 {abnormalDays.length} 天的血壓偏高，請留意家人健康狀況。
                </p>
              </div>
            </motion.div>
          )}

          {/* Trend Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-6 h-6" />
                7天血壓趨勢
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={demoData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="day" stroke="hsl(var(--muted-foreground))" />
                  <YAxis domain={[60, 180]} stroke="hsl(var(--muted-foreground))" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "0.75rem",
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="systolic"
                    name="收縮壓"
                    stroke="hsl(var(--destructive))"
                    strokeWidth={3}
                    dot={{ r: 5 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="diastolic"
                    name="舒張壓"
                    stroke="hsl(var(--primary))"
                    strokeWidth={3}
                    dot={{ r: 5 }}
                  />
                  {/* Threshold line at 140 */}
                  <Line
                    type="monotone"
                    dataKey={() => 140}
                    name="警戒線"
                    stroke="hsl(var(--bp-red))"
                    strokeDasharray="8 4"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* History Table */}
          <Card>
            <CardHeader>
              <CardTitle>📋 詳細紀錄</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="py-3 px-2 font-bold">日期</th>
                      <th className="py-3 px-2 font-bold">收縮壓</th>
                      <th className="py-3 px-2 font-bold">舒張壓</th>
                      <th className="py-3 px-2 font-bold">狀態</th>
                    </tr>
                  </thead>
                  <tbody>
                    {demoData.map((d) => {
                      const isHigh = d.systolic >= 140 || d.diastolic >= 90;
                      return (
                        <tr key={d.day} className={`border-b border-border ${isHigh ? "bg-destructive/5" : ""}`}>
                          <td className="py-3 px-2">{d.day}</td>
                          <td className="py-3 px-2 font-bold">{d.systolic}</td>
                          <td className="py-3 px-2 font-bold">{d.diastolic}</td>
                          <td className="py-3 px-2">
                            {isHigh ? (
                              <span className="text-destructive font-bold">⚠️ 偏高</span>
                            ) : (
                              <span className="text-bp-green font-bold">✅ 正常</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Back link */}
          <div className="text-center">
            <Button variant="outline" className="h-14 text-lg" onClick={() => (window.location.href = "/")}>
              ❤️ 回到量測頁面
            </Button>
          </div>
        </motion.div>
      )}

      <MedicalDisclaimer />
    </div>
  );
};

export default FamilyPortal;
