import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

serve(async (req) => {
  const { record } = await req.json();

  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${Deno.env.get("RESEND_API_KEY")}`,
    },
    body: JSON.stringify({
      from: "onboarding@resend.dev",
      to: "ivanromero.icfes500@gmail.com",
      subject: "🆕 Nuevo registro pendiente — Tutor ICFES",
      html: `
        <h2>Nuevo padre registrado</h2>
        <p><strong>Nombre:</strong> ${record.nombre}</p>
        <p><strong>Email:</strong> ${record.email}</p>
        <p><strong>Teléfono:</strong> ${record.telefono}</p>
        <p><strong>Fecha:</strong> ${record.fecha_creacion}</p>
        <br/>
        <p>Activa la cuenta en 
          <a href="https://supabase.com/dashboard">Supabase Studio</a> 
          una vez confirmes el pago.
        </p>
      `,
    }),
  });

  const resendBody = await res.json();
  console.log("Resend status:", res.status);
  console.log("Resend response:", JSON.stringify(resendBody));

  return new Response(JSON.stringify({ ok: res.ok, resend: resendBody }), {
    headers: { "Content-Type": "application/json" },
  });
});