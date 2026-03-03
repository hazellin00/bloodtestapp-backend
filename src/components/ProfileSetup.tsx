import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { motion } from "framer-motion";

export interface UserProfileData {
  id?: string;
  age: number;
  weight: number;
  height: number;
}

interface ProfileSetupProps {
  onComplete: (data: UserProfileData) => void;
}

const ProfileSetup = ({ onComplete }: ProfileSetupProps) => {
  const [age, setAge] = useState("");
  const [weight, setWeight] = useState("");
  const [height, setHeight] = useState("");

  const handleSubmit = () => {
    const a = parseInt(age);
    const w = parseFloat(weight);
    const h = parseFloat(height);

    if (isNaN(a) || isNaN(w) || isNaN(h) || a <= 0 || w <= 0 || h <= 0) return;
    onComplete({ age: a, weight: w, height: h });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card rounded-2xl p-6 shadow-sm border border-border"
    >
      <h3 className="elder-heading mb-4">👤 基本資料設定</h3>
      <p className="text-muted-foreground elder-text mb-6">
        為了給您最準確的健康與飲食建議，請輸入您的基本身高體重：
      </p>

      <div className="space-y-5">
        <div>
          <label className="elder-text font-bold block mb-2">年齡 (歲)</label>
          <Input
            type="number"
            inputMode="numeric"
            placeholder="例：70"
            value={age}
            onChange={(e) => setAge(e.target.value)}
            className="elder-text h-16 text-center text-2xl font-bold"
          />
        </div>

        <div>
          <label className="elder-text font-bold block mb-2">身高 (公分)</label>
          <Input
            type="number"
            inputMode="numeric"
            placeholder="例：170"
            value={height}
            onChange={(e) => setHeight(e.target.value)}
            className="elder-text h-16 text-center text-2xl font-bold"
          />
        </div>

        <div>
          <label className="elder-text font-bold block mb-2">體重 (公斤)</label>
          <Input
            type="number"
            inputMode="numeric"
            placeholder="例：65.5"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
            className="elder-text h-16 text-center text-2xl font-bold"
          />
        </div>

        <Button
          onClick={handleSubmit}
          disabled={!age || !weight || !height}
          className="elder-btn w-full bg-primary text-primary-foreground hover:bg-primary/90 mt-4"
        >
          ✅ 確認送出
        </Button>
      </div>
    </motion.div>
  );
};

export default ProfileSetup;
