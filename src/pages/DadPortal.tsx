import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import BPEntryForm from "@/components/BPEntryForm";
import TrafficLight from "@/components/TrafficLight";
import ProgressTracker from "@/components/ProgressTracker";
import WellnessCard from "@/components/WellnessCard";
import MedicalDisclaimer from "@/components/MedicalDisclaimer";
import { averageReadings, type BPReading } from "@/lib/bp-utils";
import { Heart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { saveHealthLog, getInsights } from "@/lib/api";
import ProfileSetup, { type UserProfileData } from "@/components/ProfileSetup";

const DadPortal = () => {
  const [currentDay, setCurrentDay] = useState(1);
  const [currentPeriod, setCurrentPeriod] = useState<"morning" | "evening">("morning");
  const [sessionIndex, setSessionIndex] = useState(1);
  const [readings, setReadings] = useState<BPReading[]>([]);
  const [showResult, setShowResult] = useState(false);
  const [aiAdvice, setAiAdvice] = useState<string | null>(null);
  const [profile, setProfile] = useState<UserProfileData | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Track completion
  const completedPeriods: Record<number, { morning: boolean; evening: boolean }> = {};
  for (let d = 1; d <= 7; d++) {
    const morningCount = readings.filter((r) => r.period === "morning" && getDay(r) === d).length;
    const eveningCount = readings.filter((r) => r.period === "evening" && getDay(r) === d).length;
    completedPeriods[d] = { morning: morningCount >= 2, evening: eveningCount >= 2 };
  }

  function getDay(r: BPReading): number {
    // Simple: assign day based on when it was recorded (using order for demo)
    const idx = readings.indexOf(r);
    return Math.floor(idx / 4) + 1; // 4 readings per day
  }

  const handleSubmit = useCallback(
    async (reading: Omit<BPReading, "timestamp">) => {
      setIsSubmitting(true);
      setSubmitError(null);

      const newReading: BPReading = {
        ...reading,
        timestamp: new Date().toISOString(),
      };
      
      const logBody = {
        user_id: profile?.id || "dad-001",
        systolic: newReading.systolic,
        diastolic: newReading.diastolic,
        heart_rate: newReading.heartRate,
        period: currentPeriod,
      };

      try {
        // Save to Supabase first
        await saveHealthLog(logBody);

        const updated = [...readings, newReading];
        setReadings(updated);
        setShowResult(true);

        // Fetch AI Insights in background
        if (profile) {
          getInsights(profile, updated)
            .then((res) => setAiAdvice(res.advice))
            .catch(console.error);
        }

        // Advance session logic
        setTimeout(() => {
          if (sessionIndex === 1) {
            setSessionIndex(2);
            setShowResult(false);
          } else {
            // Done with this period
            if (currentPeriod === "morning") {
              setCurrentPeriod("evening");
              setSessionIndex(1);
              setShowResult(false);
            } else {
              // Done with the day
              if (currentDay < 7) {
                setCurrentDay((d) => d + 1);
                setCurrentPeriod("morning");
                setSessionIndex(1);
                setShowResult(false);
              }
              // else: 7 days complete
            }
          }
        }, 3000);
      } catch (error: any) {
        console.error("Submission failed:", error);
        setSubmitError("儲存失敗，請檢查網路連線或稍後再試。 (" + (error.message || "未知錯誤") + ")");
      } finally {
        setIsSubmitting(false);
      }
    },
    [readings, sessionIndex, currentPeriod, currentDay, profile]
  );

  const lastReading = readings[readings.length - 1];
  const todayReadings = readings.slice(-4);
  const avg = averageReadings(todayReadings);

  // Fallback advice if Gemini is loading or fails
  const mockAdvice = `🥦 正在為您生成專屬健康建議... 請稍候。`;

  return (
    <div className="min-h-screen bg-background p-4 md:p-8 max-w-2xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <div className="flex items-center justify-center gap-3 mb-2">
          <Heart className="w-10 h-10 text-destructive" fill="currentColor" />
          <h1 className="elder-heading-lg">血壓健康管家</h1>
        </div>
        <p className="elder-text text-muted-foreground">每天量血壓，健康看得見</p>
      </motion.div>

      {/* Progress */}
      <div className="mb-8">
        <ProgressTracker currentDay={currentDay} completedPeriods={completedPeriods} />
      </div>

      {/* Conditionally Show Profile Setup or BP Form */}
      {!profile ? (
        <ProfileSetup onComplete={setProfile} />
      ) : (
        <>
          {/* Submit Error */}
          {submitError && (
            <motion.div 
              initial={{ opacity: 0, y: -10 }} 
              animate={{ opacity: 1, y: 0 }}
              className="bg-destructive/10 border-l-4 border-destructive p-4 mb-8 rounded-r-xl"
            >
              <p className="elder-text text-destructive font-bold">{submitError}</p>
            </motion.div>
          )}

          {/* Result or Form */}
          <AnimatePresence mode="wait">
            {showResult && lastReading ? (
              <motion.div
                key="result"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center gap-6 mb-8"
              >
                <TrafficLight systolic={lastReading.systolic} diastolic={lastReading.diastolic} />
                <p className="elder-text text-muted-foreground">{isSubmitting ? "正在儲存中..." : "儲存成功！正準備下一次紀錄"}</p>
              </motion.div>
            ) : (
              <motion.div key="form" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <BPEntryForm period={currentPeriod} sessionIndex={sessionIndex} onSubmit={handleSubmit} />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Today's Average */}
          {avg && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-card rounded-2xl p-6 border border-border shadow-sm mb-8 text-center"
            >
              <h3 className="elder-heading mb-3">📊 今日平均血壓</h3>
              <TrafficLight systolic={avg.systolic} diastolic={avg.diastolic} />
              {avg.heartRate > 0 && (
                <p className="elder-text mt-2 text-muted-foreground">心率：{avg.heartRate} bpm</p>
              )}
            </motion.div>
          )}

          {/* Wellness Card */}
          <div className="mb-8">
            <WellnessCard advice={readings.length > 0 ? (aiAdvice || mockAdvice) : null} />
          </div>
        </>
      )}

      {/* Navigation to Family Portal */}
      <div className="text-center">
        <Button
          variant="outline"
          className="elder-btn border-primary text-primary hover:bg-primary/10"
          onClick={() => (window.location.href = "/family")}
        >
          👨‍👩‍👧 家人監測入口
        </Button>
      </div>

      <MedicalDisclaimer />
    </div>
  );
};

export default DadPortal;
