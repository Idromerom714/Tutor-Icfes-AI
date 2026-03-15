## Cloudflare: mapear /ads.txt a /static/ads.txt

Si tu app Streamlit solo publica `static/ads.txt`, crea una regla de URL Rewrite en Cloudflare:

1. Ir a **Rules** -> **Transform Rules** -> **URL Rewrite Rules**.
2. Crear regla con:

- **If incoming requests match**:
  - Field: `URI Path`
  - Operator: `equals`
  - Value: `/ads.txt`
- **Then**:
  - Rewrite path to: `/static/ads.txt`

3. Guardar y desplegar la regla.

Comprobación:

```bash
curl -I https://tu-dominio.com/ads.txt
curl https://tu-dominio.com/ads.txt
```

La respuesta debe incluir exactamente:

```txt
google.com, pub-5888906096884160, DIRECT, f08c47fec0942fa0
```