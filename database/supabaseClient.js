// supabaseClient.js
import { createClient } from '@supabase/supabase-js'

// Replace these with your Supabase project's URL and anon key
const supabaseUrl = SUPABASE_URL
const supabaseKey = SUPABASE_KEY
const supabase = createClient(supabaseUrl, supabaseKey)

export default supabase