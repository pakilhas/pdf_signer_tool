from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from .forms import DocumentSignForm
from .models import SignedDocument
from .utils import process_document
import traceback
import os

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')

def home(request):
    success = False
    doc_id = None
    
    if request.method == 'POST':
        form = DocumentSignForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                document = form.save(commit=False)
                document.ip_address = get_client_ip(request)
                
                # Obter o modo de assinatura
                signature_mode = form.cleaned_data.get('signature_mode', 'manual')
                
                # Processar coordenadas apenas no modo manual
                if signature_mode == 'manual':
                    signature_x = request.POST.get('signature_x')
                    signature_y = request.POST.get('signature_y')
                    signature_page = request.POST.get('signature_page', '1')
                    
                    if signature_x and signature_y:
                        document.signature_x = float(signature_x)
                        document.signature_y = float(signature_y)
                    
                    document.signature_page = int(signature_page)
                else:
                    # Modo automático: definir valores padrão
                    document.signature_position = 'center'  # Posição padrão
                    document.signature_page = 1  # Página padrão
                    document.signature_x = None
                    document.signature_y = None
                
                document.save()
                
                signed_path = process_document(document)
                doc_id = document.id
                success = True
                
                # Obter nome original do arquivo
                original_filename = os.path.basename(document.original_file.name)
                name, ext = os.path.splitext(original_filename)
                signed_filename = f"{name}_APROVADO_CBS{ext}"
                
                # Retornar o PDF assinado para download
                response = FileResponse(open(signed_path, 'rb'), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{signed_filename}"'
                return response
                
            except Exception as e:
                traceback.print_exc()
                return render(request, 'signer/index.html', {
                    'form': form,
                    'error': f"Erro no processamento: {str(e)}"
                })
        else:
            # Formulário inválido, mostrar erros
            return render(request, 'signer/index.html', {
                'form': form,
                'error': "Por favor, corrija os erros abaixo"
            })
    
    form = DocumentSignForm()
    return render(request, 'signer/index.html', {
        'form': form,
        'success': success,
        'doc_id': doc_id
    })

def download_document(request, doc_id):
    try:
        document = SignedDocument.objects.get(id=doc_id)
        if document.signed_file:
            return FileResponse(
                open(document.signed_file.path, 'rb'),
                content_type='application/pdf',
                filename=f"documento_assinado_.pdf"
            )
        return HttpResponse("Documento não encontrado", status=404)
    
    except SignedDocument.DoesNotExist:
        return HttpResponse("Documento não encontrado", status=404)
    except Exception as e:
        traceback.print_exc()
        return HttpResponse(f"Erro interno: {str(e)}", status=500)