import { motion } from "framer-motion";

interface ProgressTrackerProps {
  currentDay: number; // 1-7
  completedPeriods: Record<number, { morning: boolean; evening: boolean }>;
}

const ProgressTracker = ({ currentDay, completedPeriods }: ProgressTrackerProps) => {
  return (
    <div className="w-full">
      <h3 className="elder-text font-bold mb-4">📅 7天量測進度</h3>
      <div className="grid grid-cols-7 gap-2">
        {Array.from({ length: 7 }, (_, i) => i + 1).map((day) => {
          const periods = completedPeriods[day] || { morning: false, evening: false };
          const isComplete = periods.morning && periods.evening;
          const isPartial = periods.morning || periods.evening;
          const isCurrent = day === currentDay;

          return (
            <motion.div
              key={day}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: day * 0.05 }}
              className={`flex flex-col items-center p-3 rounded-xl border-2 transition-all ${
                isCurrent
                  ? "border-primary bg-primary/10 shadow-md"
                  : isComplete
                  ? "border-bp-green bg-bp-green/10"
                  : isPartial
                  ? "border-bp-yellow bg-bp-yellow/5"
                  : "border-border bg-card"
              }`}
            >
              <span className="text-lg font-bold">第{day}天</span>
              <div className="flex gap-1 mt-1">
                <span className={`w-3 h-3 rounded-full ${periods.morning ? "bg-bp-green" : "bg-muted"}`} title="早" />
                <span className={`w-3 h-3 rounded-full ${periods.evening ? "bg-bp-green" : "bg-muted"}`} title="晚" />
              </div>
            </motion.div>
          );
        })}
      </div>
      <p className="text-muted-foreground mt-2 text-center">
        每天早晚各量2次，系統自動計算平均值
      </p>
    </div>
  );
};

export default ProgressTracker;
