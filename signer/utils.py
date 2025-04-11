import os
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import black
from PIL import Image
from django.conf import settings

def sign_pdf(pdf_file, signature_text=None, signature_image=None):
    """Adiciona assinatura textual e/ou imagem a um PDF de forma segura.
    
    Args:
        pdf_file: Arquivo PDF original
        signature_text: Texto da assinatura (opcional)
        signature_image: Imagem da assinatura (opcional)
    
    Returns:
        Caminho absoluto do arquivo assinado
    
    Raises:
        Exception: Com mensagem detalhada em caso de erro
    """
    output_path = None
    try:
        # Configurações ajustáveis
        config = {
            'text': {
                'font': 'Helvetica-Bold',
                'size': 12,
                'color': black,
                'margin_right': 180, #aumentar para mover para esquerda
                'margin_bottom': 50
            },
            'image': {
                'max_width': 150,
                'max_height': 50,
                'margin_right': 100, #aumentar para mover para esquerda
                'margin_bottom': 30
            },
            'output_dir': os.path.join(settings.MEDIA_ROOT, 'signed_pdfs')
        }

        # Garante que o diretório de saída existe
        os.makedirs(config['output_dir'], exist_ok=True)

        # Processamento do PDF
        with BytesIO() as output_buffer:
            pdf_reader = PdfReader(pdf_file)
            pdf_writer = PdfWriter()

            for page in pdf_reader.pages:
                packet = BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                page_width = float(page.mediabox.upper_right[0])
                page_height = float(page.mediabox.upper_right[1])

                # Assinatura textual
                if signature_text:
                    can.setFont(
                        config['text']['font'],
                        config['text']['size']
                    )
                    can.setFillColor(config['text']['color'])
                    text_x = page_width - config['text']['margin_right']
                    text_y = config['text']['margin_bottom']
                    can.drawString(text_x, text_y, signature_text)

                # Assinatura por imagem
                if signature_image:
                    with Image.open(signature_image) as img:
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Calcula dimensões mantendo proporção
                        img_ratio = img.width / img.height
                        if img_ratio > 1:
                            width = min(config['image']['max_width'], img.width)
                            height = width / img_ratio
                        else:
                            height = min(config['image']['max_height'], img.height)
                            width = height * img_ratio

                        img_x = page_width - width - config['image']['margin_right']
                        img_y = config['image']['margin_bottom']

                        can.drawImage(
                            ImageReader(img),
                            img_x,
                            img_y,
                            width=width,
                            height=height,
                            mask='auto'
                        )

                can.save()
                packet.seek(0)
                overlay = PdfReader(packet)
                page.merge_page(overlay.pages[0])
                pdf_writer.add_page(page)

            # Gera nome único para o arquivo
            output_path = os.path.join(
                config['output_dir'],
                f'signed_{os.urandom(4).hex()}.pdf'
            )

            # Escreve o conteúdo diretamente no arquivo final
            with open(output_path, 'wb') as f:
                pdf_writer.write(f)

        return os.path.abspath(output_path)

    except Exception as e:
        # Limpeza em caso de erro
        if output_path and os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass
        raise Exception(f"Erro ao assinar PDF: {str(e)}")