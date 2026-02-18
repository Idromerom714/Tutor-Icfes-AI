from fpdf import FPDF
from datetime import datetime
import io

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Resumen de Estudio - El Profe Saber', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

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
            raise ValueError("mensajes debe ser una lista no vacía")
        
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Info de cabecera
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 10, f"Materia: {materia}", 0, 1, 'L', True)
        pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, 'L', True)
        pdf.ln(10)

        # Agregar mensajes
        for msg in mensajes:
            try:
                rol = "ESTUDIANTE" if msg.get("role") == "user" else "EL PROFE SABER"
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(0, 8, f"{rol}:", 0, 1)
                
                pdf.set_font("Arial", '', 10)
                contenido = msg.get("content", "")
                
                # Limpiar caracteres problemáticos pero preservar el contenido
                contenido_limpio = (
                    contenido
                    .replace('$', '')
                    .replace('**', '')
                    .replace('###', '')
                    .replace('##', '')
                    .replace('#', '')
                )
                
                # Usar multi_cell para texto largo
                pdf.multi_cell(0, 5, contenido_limpio)
                pdf.ln(5)
                pdf.cell(0, 0, '', 'T')  # Línea separadora
                pdf.ln(5)
            except Exception as e:
                print(f"Error procesando mensaje: {e}")
                continue

        # Retornar el PDF como bytes
        pdf_output = pdf.output(dest='S')
        
        # Convertir a bytes si es necesario (puede venir como bytearray, str, o bytes)
        if isinstance(pdf_output, bytearray):
            pdf_output = bytes(pdf_output)
        elif isinstance(pdf_output, str):
            pdf_output = pdf_output.encode('latin-1')
        elif not isinstance(pdf_output, bytes):
            raise TypeError(f"Tipo inesperado de salida PDF: {type(pdf_output)}")
        
        return pdf_output
        
    except Exception as e:
        print(f"❌ Error generando PDF: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None