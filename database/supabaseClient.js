// supabaseClient.js
import { createClient } from '@supabase/supabase-js'

// Replace these with your Supabase project's URL and anon key
const supabaseUrl = 'https://tocrntktnrrrcaxtnvly.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvY3JudGt0bnJycmNheHRudmx5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzIxODA1NzksImV4cCI6MjA0Nzc1NjU3OX0.bTG7DuVYl8R-FhL3pW_uHJSYwSFClS1VO3--1eA6d-E'

const supabase = createClient(supabaseUrl, supabaseKey)

export default supabase