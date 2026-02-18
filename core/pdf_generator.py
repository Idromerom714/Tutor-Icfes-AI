from fpdf import FPDF
from datetime import datetime
import re

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 10, 'Resumen de Estudio - El Profe Saber', 0, 1, 'C')
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', '', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def generar_pdf_estudio(mensajes, materia):
    """
    Genera un PDF con los mensajes de la conversación.
    
    Args:
        mensajes: Lista de diccionarios con 'role' y 'content'
        materia: Nombre de la materia
        
    Returns:
        bytes: Contenido del PDF en bytes, o None si hay error
    """
    try:
        # Validar entrada
        if not mensajes or not isinstance(mensajes, list):
            print(f"⚠️ mensajes vacío o no es lista: {type(mensajes)}, contenido: {mensajes}")
            raise ValueError("mensajes debe ser una lista no vacía")
        
        print(f"📋 Generando PDF con {len(mensajes)} mensajes")
        
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=11)
        
        # Info de cabecera
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 8, f"Materia: {materia}", 0, 1, 'L', True)
        pdf.cell(0, 8, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, 'L', True)
        pdf.ln(8)

        # Agregar mensajes
        mensaje_count = 0
        for idx, msg in enumerate(mensajes):
            try:
                rol = "ESTUDIANTE" if msg.get("role") == "user" else "EL PROFE SABER"
                contenido = msg.get("content", "")
                
                if not contenido or not contenido.strip():
                    print(f"⚠️ Mensaje {idx} vacío o sin contenido")
                    continue
                
                print(f"✓ Procesando mensaje {idx}: {rol} ({len(contenido)} caracteres)")
                
                # Encabezado del mensaje
                pdf.set_font("Helvetica", 'B', 10)
                pdf.cell(0, 6, f"{rol}:", 0, 1)
                
                # Limpiar content: remover markdown pero preservar el texto
                contenido_limpio = limpiar_contenido(contenido)
                
                if not contenido_limpio or not contenido_limpio.strip():
                    print(f"⚠️ Contenido vacío después de limpiar")
                    continue
                
                print(f"  -> Contenido limpio: {len(contenido_limpio)} caracteres")
                
                # Cuerpo del mensaje
                pdf.set_font("Helvetica", '', 10)
                try:
                    # Sanitizar contenido de caracteres problemáticos
                    contenido_sanitizado = sanitizar_para_pdf(contenido_limpio)
                    
                    if contenido_sanitizado and contenido_sanitizado.strip():
                        # Dividir en líneas para mejor control
                        lineas = contenido_sanitizado.split('\n')
                        for linea in lineas:
                            if linea.strip():
                                try:
                                    # Usar encode/decode latin-1 para soportar acentos y ñ
                                    linea_limpia = linea.strip()[:200]
                                    # Codificar a latin-1 y volver a decodificar para asegurar compatibilidad
                                    try:
                                        linea_segura = linea_limpia.encode('latin-1', 'ignore').decode('latin-1')
                                    except:
                                        linea_segura = linea_limpia
                                    
                                    pdf.cell(0, 4, linea_segura, 0, 1)
                                except Exception as line_err:
                                    print(f"    -> Error en línea, saltando: {line_err}")
                                    continue
                    else:
                        pdf.cell(0, 4, "[Contenido sin texto]", 0, 1)
                        
                except Exception as e:
                    print(f"  -> Error en renderizado: {e}")
                    pdf.cell(0, 4, "[Error al mostrar contenido]", 0, 1)
                
                pdf.ln(3)
                
                # Línea separadora
                pdf.set_draw_color(200, 200, 200)
                pdf.cell(0, 0, '', 'T')
                pdf.ln(4)
                
                mensaje_count += 1
                
            except Exception as e:
                print(f"❌ Error procesando mensaje {idx}: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                continue

        if mensaje_count == 0:
            # Si no se pudo procesar ningún mensaje, agregar mensaje de error
            pdf.set_font("Helvetica", '', 10)
            pdf.multi_cell(0, 4, f"Nota: Se intentaron procesar {len(mensajes)} mensajes pero ninguno pudo agregarse al PDF.")

        # Retornar el PDF como bytes
        pdf_output = pdf.output(dest='S')
        
        # Convertir a bytes si es necesario
        if isinstance(pdf_output, bytearray):
            pdf_output = bytes(pdf_output)
        elif isinstance(pdf_output, str):
            pdf_output = pdf_output.encode('latin-1')
        elif not isinstance(pdf_output, bytes):
            raise TypeError(f"Tipo inesperado de salida PDF: {type(pdf_output)}")
        
        print(f"✅ PDF generado exitosamente: {len(pdf_output)} bytes, {mensaje_count} mensajes incluidos")
        return pdf_output
        
    except Exception as e:
        print(f"❌ Error CRÍTICO generando PDF: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def limpiar_contenido(texto):
    """
    Limpia el contenido de marcado Markdown y caracteres especiales problemáticos,
    preservando acentos, ñ y convirtiendo fórmulas a notación legible.
    """
    if not texto:
        return ""
    
    # Convertir fórmulas matemáticas a notación legible (NO eliminar)
    # Fórmulas en bloque: $$...$$
    texto = re.sub(r'\$\$(.+?)\$\$', r'[FORMULA] \1 [/FORMULA]', texto, flags=re.DOTALL)
    # Fórmulas inline: $...$
    texto = re.sub(r'\$(.+?)\$', r'(\1)', texto)
    
    # Remover markdown manteniendo el contenido
    texto = re.sub(r'#{1,6}\s+', '', texto)  # Headers
    texto = re.sub(r'\*\*(.+?)\*\*', r'\1', texto)  # Bold
    texto = re.sub(r'\*(.+?)\*', r'\1', texto)  # Italic
    texto = re.sub(r'__(.+?)__', r'\1', texto)  # Bold
    texto = re.sub(r'_(.+?)_', r'\1', texto)  # Italic
    texto = re.sub(r'`(.+?)`', r'\1', texto)  # Inline code
    
    # Remover listas (pero preservar el contenido)
    texto = re.sub(r'^[\*\-\+]\s+', '', texto, flags=re.MULTILINE)
    texto = re.sub(r'^\d+\.\s+', '', texto, flags=re.MULTILINE)
    
    # Remover tabla markdown
    texto = re.sub(r'\|.*\|', '', texto, flags=re.MULTILINE)
    
    # Normalizar espacios
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    texto = re.sub(r' {2,}', ' ', texto)
    
    return texto.strip()


def sanitizar_para_pdf(texto):
    """
    Sanitiza texto para que sea compatible con FPDF y Helvetica.
    PRESERVA acentos (á, é, í, ó, ú) y ñ.
    Solo reemplaza caracteres verdaderamente problemáticos.
    """
    if not texto:
        return ""
    
    # Reemplazos SOLO de caracteres verdaderamente problemáticos
    reemplazos = {
        '–': '-',      # En dash
        '—': '-',      # Em dash
        '…': '...',    # Elipsis
        '√': 'raiz',   # Raíz cuadrada
        '∫': 'integral', # Integral
        '∞': 'infinito', # Infinito
        '≈': '~',      # Aproximado
        '≠': '!=',     # No igual
        '≤': '<=',     # Menor o igual
        '≥': '>=',     # Mayor o igual
        '×': 'x',      # Multiplicación
        '÷': '/',      # División
        '⁰': '0',      # Superíndice
        '¹': '1',      # Superíndice
        '²': '2',      # Superíndice
        '³': '3',      # Superíndice
    }
    
    for original, reemplazo in reemplazos.items():
        texto = texto.replace(original, reemplazo)
    
    # Remover SOLO emojis y caracteres de control verdaderamente problemáticos
    # Preservar: acentos, ñ, caracteres latinos
    texto_limpio = []
    for char in texto:
        code = ord(char)
        # Mantener ASCII regular (32-126) y caracteres latinos extendidos (160-255)
        if (32 <= code <= 126) or (160 <= code <= 255) or code == 10 or code == 13:
            texto_limpio.append(char)
        # Si es un emoji o símbolo raro, saltarlo pero mantener espacio
        else:
            if char not in ' ':
                texto_limpio.append(' ')
    
    texto = ''.join(texto_limpio)
    
    # Normalizar espacios múltiples
    texto = re.sub(r' {2,}', ' ', texto)
    
    return texto.strip()