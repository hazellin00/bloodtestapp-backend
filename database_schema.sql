-- Supabase Schema for Health Tracker

-- 1. Profiles Table
CREATE TABLE IF NOT EXISTS public.profiles (
  id uuid NOT NULL PRIMARY KEY, -- Matches up with Supabase auth users
  role text NOT NULL CHECK (role IN ('dad', 'daughter')),
  family_id text NOT NULL,
  height numeric NULL,
  weight numeric NULL,
  age integer NULL,
  created_at timestamptz DEFAULT now()
);

-- 2. Health Logs Table
CREATE TABLE IF NOT EXISTS public.health_logs (
  id uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  systolic integer NOT NULL,
  diastolic integer NOT NULL,
  heart_rate integer NOT NULL,
  period text NOT NULL CHECK (period IN ('morning', 'evening')),
  created_at timestamptz DEFAULT now()
);

-- 3. Family Links Table
CREATE TABLE IF NOT EXISTS public.family_links (
  id uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
  parent_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  child_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  created_at timestamptz DEFAULT now(),
  UNIQUE (parent_id, child_id)
);

-- Configure RLS to make it securely accessible assuming we aren't just bypassing in the FastAPI backend
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.health_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.family_links ENABLE ROW LEVEL SECURITY;

-- If your FastAPI is using a service key to connect, RLS is bypassed.
-- But if we connect directly from UI with Anon key or FastAPI with Anon key, we need policies.
-- We'll assume FastAPI is using service-role or that you can adapt RLS below.
CREATE POLICY "Enable all for all users (TEMP)" ON public.profiles FOR ALL USING (true);
CREATE POLICY "Enable all for all users (TEMP)" ON public.health_logs FOR ALL USING (true);
CREATE POLICY "Enable all for all users (TEMP)" ON public.family_links FOR ALL USING (true);

