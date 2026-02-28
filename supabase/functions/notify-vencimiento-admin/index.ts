import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

serve(async (_req) => {
  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
  );

  // Obtener cuentas vencidas hoy
  const { data: vencidos } = await supabase
    .from("padres")
    .select("nombre, email, plan")
    .eq("estado", "pendiente_renovacion")
    .eq("fecha_vencimiento", new Date().toISOString().split("T")[0]);

  if (!vencidos || vencidos.length === 0) {
    return new Response(JSON.stringify({ msg: "Sin vencimientos hoy" }));
  }

  const lista = vencidos.map(p =>
    `<li><strong>${p.nombre}</strong> — ${p.email} (Plan: ${p.plan})</li>`
  ).join("");

  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${Deno.env.get("RESEND_API_KEY")}`,
    },
    body: JSON.stringify({
      from: "onboarding@resend.dev",
      to: "ivanromero714@gmail.com",
      subject: `⚠️ ${vencidos.length} cuenta(s) vencida(s) hoy — Tutor ICFES`,
      html: `
        <h2>Cuentas vencidas hoy</h2>
        <ul>${lista}</ul>
        <p>Contacta a estos padres para gestionar la renovación.</p>
      `,
    }),
  });

  const body = await res.json();
  console.log("Resend:", res.status, JSON.stringify(body));

  return new Response(JSON.stringify({ ok: res.ok, vencidos: vencidos.length }));
});