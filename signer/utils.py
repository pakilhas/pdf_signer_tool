from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
import PyPDF2
import os
from io import BytesIO

def process_document(document):
    output_dir = os.path.join(settings.MEDIA_ROOT, 'processed')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'doc_{document.id}.pdf')

    try:
        # ===== CONFIGURAÇÕES DE TAMANHO =====
        MAX_IMAGE_WIDTH = 150    # Largura máxima da imagem
        MAX_IMAGE_HEIGHT = 60    # Altura máxima da imagem
        FONT_SIZE = 10           # Tamanho do texto
        MARGIN_BOTTOM = 40       # Margem inferior
        # =====================================

        with open(document.watermark_image.path, 'rb') as wm_file:
            watermark_img = ImageReader(wm_file)
            original_pdf = PyPDF2.PdfReader(document.original_file.open())
            num_pages = len(original_pdf.pages)

            packet = BytesIO()
            c = canvas.Canvas(packet, pagesize=letter)

            for _ in range(num_pages):
                # Redimensionar imagem
                img_width, img_height = watermark_img.getSize()
                aspect = img_height / float(img_width)
                
                if img_width > MAX_IMAGE_WIDTH:
                    img_width = MAX_IMAGE_WIDTH
                    img_height = MAX_IMAGE_WIDTH * aspect
                if img_height > MAX_IMAGE_HEIGHT:
                    img_height = MAX_IMAGE_HEIGHT
                    img_width = MAX_IMAGE_HEIGHT / aspect

                # Posicionamento
                page_width = letter[0]
                positions = {
                    'left': 50,
                    'center': (page_width - img_width) / 2,
                    'right': page_width - img_width - 50
                }
                x_pos = positions.get(document.signature_position, 50)
                y_pos = MARGIN_BOTTOM

                # Desenhar imagem
                c.setFillAlpha(document.watermark_opacity)
                c.drawImage(
                    watermark_img,
                    x_pos,
                    y_pos,
                    width=img_width,
                    height=img_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
                c.setFillAlpha(1)

                # Desenhar texto
                if document.signature_text:
                    c.setFont("Helvetica-Bold", FONT_SIZE)
                    text = document.signature_text
                    text_width = c.stringWidth(text, "Helvetica-Bold", FONT_SIZE)
                    
                    text_x = x_pos + (img_width - text_width) / 2
                    text_y = y_pos + (img_height / 2) - (FONT_SIZE/2)  # Centralização vertical
                    
                    c.drawString(text_x, text_y, text)

                c.showPage()

            c.save()

            # Mesclar PDFs
            watermark_pdf = PyPDF2.PdfReader(packet)
            output_pdf = PyPDF2.PdfWriter()

            for page_num in range(num_pages):
                page = original_pdf.pages[page_num]
                if page_num < len(watermark_pdf.pages):
                    page.merge_page(watermark_pdf.pages[page_num])
                output_pdf.add_page(page)

            with open(output_path, 'wb') as f:
                output_pdf.write(f)

            document.signed_file.name = os.path.join('processed', f'doc_{document.id}.pdf')
            document.save()

            return output_path

    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        raise e