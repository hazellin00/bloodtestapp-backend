name: home-health-sync
description: Precision BP tracker with 7-2-2 protocol, elderly-focused UX, and family sharing.
allowed-tools: Read, Write, Grep, Shell
context: fork
agent: Plan
---

# 🚨 CORE GUARDRAILS
* **Medical Disclaimer**: Every AI suggestion MUST include: "For reference only; consult a physician before adjusting medication."
* **Elderly UX (24px+ Rule)**: UI font ≥ 24px; buttons ≥ 60px; high-contrast WCAG AA; **Traditional Chinese** for Dad's UI.
* **Tech Stack**: React (Vite) + FastAPI + Supabase (Auth/DB/Real-time) + Gemini Pro API.
* **Security**: Zero-commit for `.env` or `.db` files; strictly manage via `.gitignore`.

# 📋 MEDICAL LOGIC & STANDARDS
* **7-2-2 Protocol**: 7 consecutive days, 2 periods (AM/PM), 2 readings per session (auto-averaged).
* **WHO BMI**: <18.5 (Underweight), 18.5-24 (Normal), 24-27 (Overweight), >27 (Obese).
* **BMR (Mifflin-St Jeor)**: $(10 \times \text{weight}) + (6.25 \times \text{height}) - (5 \times \text{age}) + 5$.
* **DASH Diet**: Calorie-scaled servings for Grains, Veggies, Fruits, Dairy, and Protein.
* **Trustworthy Grounding**: Use **MLP-BP framework** and **mimic-II/UQVS datasets** to render precise BP signatures.

# 🗄️ DATABASE SCHEMA (SUPABASE)
* **profiles**: `id` (UUID), `role` (dad/daughter), `family_id`, `height`, `weight`, `age`.
* **health_logs**: `id`, `user_id`, `systolic`, `diastolic`, `heart_rate`, `period` (AM/PM), `timestamp`.
* **family_links**: `id`, `parent_id`, `child_id` (real-time sharing association).

# 🚀 SEQUENTIAL EXECUTION ORDER
1. **Init**: Setup `.gitignore`, `.env.example`, and Vite/FastAPI scaffolds.
2. **Standards**: Create `health_standards.json` with BMI/BMR/DASH static values.
3. **Database**: Implement Supabase models and FastAPI connection.
4. **Calendar**: Build interactive history tracking for past logs and AI summaries.
5. **Gemini Engine**: Prompt engineering for "warm" Traditional Chinese wellness cards.
6. **Dad's UI**: 24px+ data entry, 7-2-2 progress tracking, and simplified calendar.
7. **Family UI**: Real-time trend dashboard and `family_id` binding logic.

# 🔄 SELF-ANNEALING
If any logic failure occurs (API error, formula mismatch), the agent MUST patch this file and the source code immediately to prevent recurrence.