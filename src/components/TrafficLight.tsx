import { motion } from "framer-motion";
import { classifyBP, getBPColor, getBPLabel, type BPLevel } from "@/lib/bp-utils";

interface TrafficLightProps {
  systolic: number;
  diastolic: number;
}

const bgMap: Record<BPLevel, string> = {
  normal: "bg-bp-green",
  elevated: "bg-bp-yellow",
  high1: "bg-bp-orange",
  high2: "bg-bp-red",
  crisis: "bg-bp-red",
};

const TrafficLight = ({ systolic, diastolic }: TrafficLightProps) => {
  const level = classifyBP(systolic, diastolic);
  const label = getBPLabel(level);

  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="flex flex-col items-center gap-4"
    >
      <motion.div
        animate={{ scale: [1, 1.08, 1] }}
        transition={{ repeat: Infinity, duration: 2 }}
        className={`${bgMap[level]} w-32 h-32 rounded-full flex items-center justify-center shadow-lg`}
      >
        <span className="text-4xl font-black text-primary-foreground">
          {systolic}/{diastolic}
        </span>
      </motion.div>
      <span className="elder-text font-bold">{label}</span>
    </motion.div>
  );
};

export default TrafficLight;
