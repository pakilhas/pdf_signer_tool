import os
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import black
from PIL import Image, ImageEnhance
from django.conf import settings

def process_document(document_instance):
    """Processa o documento com marca d'água exatamente no local da assinatura"""
    try:
        # Configurações
        config = {
            'watermark': {
                'opacity': document_instance.watermark_opacity,
                'size_ratio': 1.2  # Tamanho relativo à assinatura
            },
            'signature': {
                'text_font': 'Helvetica-Bold',
                'text_size': 12,
                'text_color': black,
                'text_margin_right': 180,
                'text_margin_bottom': 50,
                'image_max_width': 150,
                'image_max_height': 50,
                'image_margin_right': 100,
                'image_margin_bottom': 30
            },
            'output_dir': os.path.join(settings.MEDIA_ROOT, 'signed_documents')
        }

        os.makedirs(config['output_dir'], exist_ok=True)

        # Caminhos dos arquivos
        input_path = document_instance.original_file.path
        watermark_path = document_instance.watermark_image.path
        signature_image_path = document_instance.signature_image.path if document_instance.signature_image else None
        output_filename = f'signed_{os.path.basename(input_path)}'
        output_path = os.path.join(config['output_dir'], output_filename)

        with open(input_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            pdf_writer = PdfWriter()

            for page in pdf_reader.pages:
                page_width = float(page.mediabox.upper_right[0])
                page_height = float(page.mediabox.upper_right[1])
                
                # 1. Determina posição e tamanho da assinatura
                if signature_image_path and os.path.exists(signature_image_path):
                    with Image.open(signature_image_path) as img:
                        img_ratio = img.width / img.height
                        if img_ratio > 1:
                            width = min(config['signature']['image_max_width'], img.width)
                            height = width / img_ratio
                        else:
                            height = min(config['signature']['image_max_height'], img.height)
                            width = height * img_ratio
                        
                        pos_x = page_width - width - config['signature']['image_margin_right']
                        pos_y = config['signature']['image_margin_bottom']
                else:
                    # Se não houver imagem, usa posição do texto
                    width = 100  # Largura estimada para texto
                    height = 40   # Altura estimada para texto
                    pos_x = page_width - config['signature']['text_margin_right']
                    pos_y = config['signature']['text_margin_bottom']

                # 2. Cria camada única com marca d'água e assinatura
                packet = BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                
                # Adiciona MARCA D'ÁGUA (primeiro - fundo)
                if watermark_path:
                    with Image.open(watermark_path) as img:
                        # Aplica transparência
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        
                        alpha = img.split()[3]
                        alpha = ImageEnhance.Brightness(alpha).enhance(config['watermark']['opacity'])
                        img.putalpha(alpha)
                        
                        # Calcula tamanho proporcional à assinatura
                        wm_width = width * config['watermark']['size_ratio']
                        wm_height = height * config['watermark']['size_ratio']
                        
                        # Centraliza a marca d'água com a assinatura
                        wm_x = pos_x - (wm_width - width)/2
                        wm_y = pos_y - (wm_height - height)/2
                        
                        can.drawImage(
                            ImageReader(img),
                            wm_x,
                            wm_y,
                            width=wm_width,
                            height=wm_height,
                            mask='auto'
                        )
                
                # Adiciona ASSINATURA (por cima da marca d'água)
                if document_instance.signature_text:
                    can.setFont(config['signature']['text_font'], config['signature']['text_size'])
                    can.setFillColor(config['signature']['text_color'])
                    can.drawString(pos_x, pos_y, document_instance.signature_text)
                
                if signature_image_path and os.path.exists(signature_image_path):
                    with Image.open(signature_image_path) as img:
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        can.drawImage(
                            ImageReader(img),
                            pos_x,
                            pos_y,
                            width=width,
                            height=height,
                            mask='auto'
                        )
                
                can.save()
                packet.seek(0)
                overlay = PdfReader(packet)
                page.merge_page(overlay.pages[0])
                pdf_writer.add_page(page)

            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)

        document_instance.signed_file.name = os.path.join('signed_documents', output_filename)
        document_instance.status = 'completed'
        document_instance.save()

        return output_path

    except Exception as e:
        document_instance.status = 'failed'
        document_instance.save()
        raise Exception(f"Erro ao processar documento: {str(e)}")