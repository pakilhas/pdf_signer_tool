from django.conf import settings
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
import PyPDF2
import os
from io import BytesIO

def process_document(document):
    # Configuração do diretório de saída
    output_dir = os.path.join(settings.MEDIA_ROOT, 'processed')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'doc_{document.id}.pdf')

    try:
        # ===== CONFIGURAÇÕES FIXAS =====
        WATERMARK_IMAGE = os.path.join(
            settings.BASE_DIR,
            'signer',
            'static',
            'img',
            'fixed_watermark.png'
        )
        OPACIDADE_FIXA = 0.3
        
        # Verificar se a imagem fixa existe
        if not os.path.exists(WATERMARK_IMAGE):
            raise FileNotFoundError(
                f"Imagem de assinatura fixa não encontrada em: {WATERMARK_IMAGE}\n"
                "Verifique o caminho e as permissões!"
            )

        # ===== PARÂMETROS DE FORMATAÇÃO =====
        MAX_IMAGE_WIDTH = 150
        MAX_IMAGE_HEIGHT = 60
        FONT_SIZE = 10
        FONT_NAME = "Helvetica-Bold"
        ESPACO_TEXTO_IMAGEM = -60
        # =====================================

        # Carregar recursos
        watermark_img = ImageReader(WATERMARK_IMAGE)
        original_pdf = PyPDF2.PdfReader(document.original_file.open())
        num_pages = len(original_pdf.pages)

        # Obter dimensões da imagem
        img_width, img_height = watermark_img.getSize()
        aspect = img_height / float(img_width)
        if img_width > MAX_IMAGE_WIDTH:
            img_width = MAX_IMAGE_WIDTH
            img_height = MAX_IMAGE_WIDTH * aspect
        if img_height > MAX_IMAGE_HEIGHT:
            img_height = MAX_IMAGE_HEIGHT
            img_width = MAX_IMAGE_HEIGHT / aspect

        # Criar PDF de saída
        output_pdf = PyPDF2.PdfWriter()

        # Processar cada página individualmente
        for page_num in range(num_pages):
            page = original_pdf.pages[page_num]
            
            # Obter tamanho real da página
            media_box = page.mediabox
            page_width = float(media_box[2] - media_box[0])
            page_height = float(media_box[3] - media_box[1])
            
            # Calcular posição base
            if document.signature_x and document.signature_y:
                # Usar coordenadas relativas (%)
                base_x = (float(document.signature_x) / 100) * page_width
                base_y = page_height - (float(document.signature_y) / 100) * page_height
            else:
                # Posição padrão
                positions = {
                    'left': 50,
                    'center': page_width / 2,
                    'right': page_width - 150
                }
                base_x = positions.get(document.signature_position, 50)
                base_y = 50

            # Calcular posições (imagem acima, texto abaixo)
            image_x = base_x - (img_width / 2)
            image_y = base_y
            text_y = base_y - img_height - ESPACO_TEXTO_IMAGEM

            # Criar camadas para esta página
            watermark_packet = BytesIO()
            watermark_canvas = canvas.Canvas(watermark_packet, pagesize=(page_width, page_height))
            
            signature_packet = BytesIO()
            signature_canvas = canvas.Canvas(signature_packet, pagesize=(page_width, page_height))

            # Desenhar imagem
            watermark_canvas.setFillAlpha(OPACIDADE_FIXA)
            watermark_canvas.drawImage(
                watermark_img,
                image_x,
                image_y,
                width=img_width,
                height=img_height,
                preserveAspectRatio=True,
                mask='auto'
            )
            watermark_canvas.setFillAlpha(1)
            watermark_canvas.showPage()
            watermark_canvas.save()

            # Desenhar texto
            if document.signature_text:
                signature_canvas.setFont(FONT_NAME, FONT_SIZE)
                text_width = signature_canvas.stringWidth(document.signature_text, FONT_NAME, FONT_SIZE)
                text_x = base_x - (text_width / 2)
                signature_canvas.drawString(text_x, text_y, document.signature_text)
            signature_canvas.showPage()
            signature_canvas.save()

            # Mesclar camadas
            watermark_packet.seek(0)
            watermark_pdf = PyPDF2.PdfReader(watermark_packet)
            
            signature_packet.seek(0)
            signature_pdf = PyPDF2.PdfReader(signature_packet) if document.signature_text else None

            # Aplicar camadas à página original
            page.merge_page(watermark_pdf.pages[0])
            if signature_pdf:
                page.merge_page(signature_pdf.pages[0])
            
            output_pdf.add_page(page)

        # Salvar arquivo final
        with open(output_path, 'wb') as f:
            output_pdf.write(f)

        # Atualizar modelo
        document.signed_file.name = os.path.join('processed', f'doc_{document.id}.pdf')
        document.save()

        return output_path

    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        import traceback
        traceback.print_exc()
        raise e