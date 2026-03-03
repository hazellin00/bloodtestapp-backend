import { motion } from "framer-motion";
import MedicalDisclaimer from "./MedicalDisclaimer";

interface WellnessCardProps {
  advice: string | null;
  loading?: boolean;
}

const WellnessCard = ({ advice, loading }: WellnessCardProps) => {
  if (loading) {
    return (
      <div className="bg-card rounded-2xl p-6 border border-border animate-pulse">
        <div className="h-6 bg-muted rounded w-3/4 mb-4" />
        <div className="h-4 bg-muted rounded w-full mb-2" />
        <div className="h-4 bg-muted rounded w-5/6 mb-2" />
        <div className="h-4 bg-muted rounded w-2/3" />
      </div>
    );
  }

  if (!advice) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card rounded-2xl p-6 border border-border shadow-sm"
    >
      <h3 className="elder-heading mb-4">🥗 今日健康建議</h3>
      <div className="elder-text whitespace-pre-line leading-relaxed">
        {advice}
      </div>
      <MedicalDisclaimer />
    </motion.div>
  );
};

export default WellnessCard;
