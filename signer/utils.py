import os
from django.conf import settings
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import PyPDF2

from reportlab.lib.units import mm
def process_document(document):
    output_dir = os.path.join(settings.MEDIA_ROOT, 'processed')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'doc_{document.id}.pdf')

    try:
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)
        
        # Posições para rodapé (85mm da base)
        positions = {
            'left': 20*mm,
            'center': (letter[0]/2) - 25*mm,  # Centralizado considerando largura de 50mm
            'right': letter[0] - 70*mm
        }
        x_pos = positions.get(document.signature_position, 20*mm)
        y_pos = 30*mm  # 30mm da borda inferior

        # Marca d'água e assinatura na mesma posição
        if document.watermark_image:
            watermark = ImageReader(document.watermark_image)
            c.setFillAlpha(document.watermark_opacity)
            c.drawImage(
                watermark,
                x_pos,
                y_pos,
                width=50*mm,
                height=20*mm,
                preserveAspectRatio=True
        )
    
        
            if document.signature_text:
                c.setFillAlpha(1)
                c.setFont("Helvetica-Bold", 12)
                c.drawString(x_pos, y_pos + 5*mm, document.signature_text)

        c.save()

        # Mesclagem com o PDF original
        original_pdf = PyPDF2.PdfReader(document.original_file)
        watermark_pdf = PyPDF2.PdfReader(packet)
        
        output = PyPDF2.PdfWriter()
        for i in range(len(original_pdf.pages)):
            page = original_pdf.pages[i]
            if i < len(watermark_pdf.pages):
                page.merge_page(watermark_pdf.pages[i])
            output.add_page(page)
        
        with open(output_path, 'wb') as f:
            output.write(f)
        
        document.signed_file.name = os.path.join('processed', f'doc_{document.id}.pdf')
        document.save()
        
        return output_path
    
    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        raise e