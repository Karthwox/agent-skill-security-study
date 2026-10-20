"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";

export default function LoginPage() {
  const supabase = createClient();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  async function signIn() {
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) setMessage(error.message);
    else window.location.href = "/";
  }

  async function signUp() {
    const { error } = await supabase.auth.signUp({ email, password });
    setMessage(error ? error.message : "Check your email to confirm your account.");
  }

  return (
    <main>
      <h1>Sign in</h1>
      <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button onClick={signIn}>Sign in</button>
      <button onClick={signUp}>Sign up</button>
      <p>{message}</p>
    </main>
  );
}
