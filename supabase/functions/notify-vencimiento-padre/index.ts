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

  // Enviar correo individual a cada padre
  for (const padre of vencidos) {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${Deno.env.get("RESEND_API_KEY")}`,
      },
      body: JSON.stringify({
        from: "onboarding@resend.dev",
        to: "ivanromero714@gmail.com", // temporal hasta tener dominio
        subject: "📅 Tu plan de Tutor ICFES ha vencido",
        html: `
          <h2>Hola ${padre.nombre},</h2>
          <p>Tu plan <strong>${padre.plan}</strong> en Tutor ICFES ha vencido hoy.</p>
          <p>Para renovar y que tu hijo pueda seguir estudiando, 
             escríbenos a <a href="mailto:ivanromero714@gmail.com">
             ivanromero714@gmail.com</a>.</p>
          <br/>
          <p>¡El ICFES se acerca, no pierdas el ritmo!</p>
        `,
      }),
    });
    const body = await res.json();
    console.log(`Padre ${padre.email}:`, res.status, JSON.stringify(body));
  }

  return new Response(JSON.stringify({ ok: true, notificados: vencidos.length }));
});