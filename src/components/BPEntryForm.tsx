import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { motion } from "framer-motion";
import type { BPReading } from "@/lib/bp-utils";

interface BPEntryFormProps {
  period: "morning" | "evening";
  sessionIndex: number; // 1 or 2
  onSubmit: (reading: Omit<BPReading, "timestamp">) => void;
}

const BPEntryForm = ({ period, sessionIndex, onSubmit }: BPEntryFormProps) => {
  const [systolic, setSystolic] = useState("");
  const [diastolic, setDiastolic] = useState("");
  const [heartRate, setHeartRate] = useState("");

  const periodLabel = period === "morning" ? "🌅 早上" : "🌙 晚上";

  const handleSubmit = () => {
    const s = parseInt(systolic);
    const d = parseInt(diastolic);
    const hr = heartRate ? parseInt(heartRate) : undefined;
    if (isNaN(s) || isNaN(d) || s < 60 || s > 260 || d < 30 || d > 160) return;
    onSubmit({ systolic: s, diastolic: d, heartRate: hr, period, sessionIndex });
    setSystolic("");
    setDiastolic("");
    setHeartRate("");
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-card rounded-2xl p-6 shadow-sm border border-border"
    >
      <h3 className="elder-heading mb-2">
        {periodLabel} — 第 {sessionIndex} 次量測
      </h3>
      <p className="text-muted-foreground elder-text mb-6">請輸入血壓計上的數值</p>

      <div className="space-y-5">
        <div>
          <label className="elder-text font-bold block mb-2">收縮壓（上壓）</label>
          <Input
            type="number"
            inputMode="numeric"
            placeholder="例：125"
            value={systolic}
            onChange={(e) => setSystolic(e.target.value)}
            className="elder-text h-16 text-center text-2xl font-bold"
          />
        </div>

        <div>
          <label className="elder-text font-bold block mb-2">舒張壓（下壓）</label>
          <Input
            type="number"
            inputMode="numeric"
            placeholder="例：82"
            value={diastolic}
            onChange={(e) => setDiastolic(e.target.value)}
            className="elder-text h-16 text-center text-2xl font-bold"
          />
        </div>

        <div>
          <label className="elder-text font-bold block mb-2">心率（選填）</label>
          <Input
            type="number"
            inputMode="numeric"
            placeholder="例：72"
            value={heartRate}
            onChange={(e) => setHeartRate(e.target.value)}
            className="elder-text h-16 text-center text-2xl font-bold"
          />
        </div>

        <Button
          onClick={handleSubmit}
          disabled={!systolic || !diastolic}
          className="elder-btn w-full bg-primary text-primary-foreground hover:bg-primary/90"
        >
          ✅ 送出紀錄
        </Button>
      </div>
    </motion.div>
  );
};

export default BPEntryForm;
