from fpdf import FPDF
from datetime import datetime
import re

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Usar embedding de fuente para soportar más caracteres
        self.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
    
    def header(self):
        self.set_font('DejaVu', '', 14)
        self.cell(0, 10, 'Resumen de Estudio - El Profe Saber', 0, 1, 'C')
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)
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
            print(f"⚠️ mensajes vacío o no es lista: {type(mensajes)}")
            raise ValueError("mensajes debe ser una lista no vacía")
        
        print(f"📋 Generando PDF con {len(mensajes)} mensajes")
        
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("DejaVu", size=11)
        
        # Info de cabecera
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 8, f"Materia: {materia}", 0, 1, 'L', True)
        pdf.cell(0, 8, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, 'L', True)
        pdf.ln(8)

        # Agregar mensajes
        for idx, msg in enumerate(mensajes):
            try:
                rol = "ESTUDIANTE" if msg.get("role") == "user" else "EL PROFE SABER"
                contenido = msg.get("content", "")
                
                if not contenido:
                    print(f"⚠️ Mensaje {idx} vacío")
                    continue
                
                print(f"✓ Procesando mensaje {idx}: {rol} ({len(contenido)} caracteres)")
                
                # Encabezado del mensaje
                pdf.set_font("DejaVu", 'B', 10)
                pdf.cell(0, 6, f"{rol}:", 0, 1)
                
                # Limpiar content: remover markdown pero preservar el texto
                contenido_limpio = limpiar_contenido(contenido)
                
                # Cuerpo del mensaje
                pdf.set_font("DejaVu", '', 10)
                pdf.multi_cell(0, 4, contenido_limpio)
                pdf.ln(3)
                
                # Línea separadora
                pdf.set_draw_color(200, 200, 200)
                pdf.cell(0, 0, '', 'T')
                pdf.ln(4)
                
            except Exception as e:
                print(f"❌ Error procesando mensaje {idx}: {e}")
                continue

        # Retornar el PDF como bytes
        pdf_output = pdf.output(dest='S')
        
        # Convertir a bytes si es necesario
        if isinstance(pdf_output, bytearray):
            pdf_output = bytes(pdf_output)
        elif isinstance(pdf_output, str):
            pdf_output = pdf_output.encode('latin-1')
        elif not isinstance(pdf_output, bytes):
            raise TypeError(f"Tipo inesperado de salida PDF: {type(pdf_output)}")
        
        print(f"✅ PDF generado exitosamente: {len(pdf_output)} bytes")
        return pdf_output
        
    except Exception as e:
        print(f"❌ Error generando PDF: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def limpiar_contenido(texto):
    """
    Limpia el contenido de marcado Markdown y caracteres especiales problemáticos,
    preservando el texto útil.
    """
    # Remover fórmulas math inline y bloques
    texto = re.sub(r'\$\$.*?\$\$', '', texto, flags=re.DOTALL)  # Bloques $$..$$
    texto = re.sub(r'\$.*?\$', '', texto)  # Inline $...$
    
    # Remover markdown
    texto = re.sub(r'#{1,6}\s+', '', texto)  # Headers
    texto = re.sub(r'\*\*(.+?)\*\*', r'\1', texto)  # Bold
    texto = re.sub(r'\*(.+?)\*', r'\1', texto)  # Italic
    texto = re.sub(r'__(.+?)__', r'\1', texto)  # Bold
    texto = re.sub(r'_(.+?)_', r'\1', texto)  # Italic
    texto = re.sub(r'`(.+?)`', r'\1', texto)  # Inline code
    
    # Remover listas (pero preservar el contenido)
    texto = re.sub(r'^[\*\-\+]\s+', '', texto, flags=re.MULTILINE)  # Bullet points
    texto = re.sub(r'^\d+\.\s+', '', texto, flags=re.MULTILINE)  # Numbered lists
    
    # Remover caracteres especiales problemáticos
    # Pero preservar acentos, emojis comunes
    texto = texto.replace('\u200b', '')  # Zero-width space
    texto = texto.replace('\u200e', '')  # Right-to-left mark
    
    # Normalizar saltos de línea
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    
    return texto.strip()