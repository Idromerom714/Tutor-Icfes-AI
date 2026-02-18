from fpdf import FPDF
from datetime import datetime

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
    try:
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Info de cabecera
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 10, f"Materia: {materia}", 0, 1, 'L', True)
        pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'L', True)
        pdf.ln(10)

        for msg in mensajes:
            rol = "ESTUDIANTE" if msg["role"] == "user" else "EL PROFE SABER"
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 8, f"{rol}:", 0, 1)
            
            pdf.set_font("Arial", '', 10)
            contenido_limpio = msg["content"].replace('$', '').replace('**', '').replace('###', '')
            pdf.multi_cell(0, 5, contenido_limpio)
            pdf.ln(5)
            pdf.cell(0, 0, '', 'T')
            pdf.ln(5)

        return pdf.output(dest='S')
    except Exception as e:
        print(f"Error generando PDF: {e}")
        return None