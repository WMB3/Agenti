import { createClient } from '@supabase/supabase-js'

// --- Configuration ---
// These variables must be in your .env.local file.
// If missing, we provide a dummy string to prevent the app from crashing on boot.
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL 
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || supabaseUrl === 'your-project-url') {
  console.warn("Supabase Configuration Missing: Please set VITE_SUPABASE_URL in .env.local")
}

// Fallback to empty strings if undefined to prevent constructor crash
export const supabase = createClient(
  supabaseUrl || 'https://placeholder.supabase.co', 
  supabaseAnonKey || 'placeholder-key'
)
