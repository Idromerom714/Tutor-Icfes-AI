import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

serve(async (req) => {
  const { record } = await req.json();

  // Solo disparar cuando el estado cambia a 'activo'
  if (record.estado !== "activo") {
    return new Response(JSON.stringify({ skipped: true }), {
      headers: { "Content-Type": "application/json" },
    });
  }

  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${Deno.env.get("RESEND_API_KEY")}`,
    },
    body: JSON.stringify({
      from: "onboarding@resend.dev",
      to: record.email,
      subject: "✅ Tu cuenta en Tutor ICFES está activa",
      html: `
        <h2>¡Bienvenido a Tutor ICFES!</h2>
        <p>Hola ${record.nombre},</p>
        <p>Tu cuenta ha sido activada. Ya puedes ingresar a la plataforma 
           con tu correo y PIN.</p>
        <br/>
        <p>Si tienes alguna pregunta escríbenos a 
           ivanromero.icfes500@gmail.com</p>
        <br/>
        <p>¡Mucho éxito en la preparación!</p>
      `,
    }),
  });
  
const resendBody = await res.json();
console.log("Resend status:", res.status);
console.log("Resend response:", JSON.stringify(resendBody));

  return new Response(JSON.stringify({ ok: res.ok }), {
    headers: { "Content-Type": "application/json" },
  });
});
