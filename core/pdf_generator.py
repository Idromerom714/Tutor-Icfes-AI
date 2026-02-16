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
        # Multi_cell para que el texto largo no se salga de la hoja
        pdf.multi_cell(0, 5, msg["content"].encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(5)
        pdf.cell(0, 0, '', 'T') # Línea divisoria
        pdf.ln(5)

    return pdf.output(dest='S') # Retorna los bytes del PDF