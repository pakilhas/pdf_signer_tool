from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse
from .forms import DocumentSignForm
from .models import SignedDocument
from .utils import process_document
import os
from django.conf import settings
import traceback
from django.urls import reverse

def get_client_ip(request):
    """Obtém o IP do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

def home(request):
    success = False
    doc_id = None
    
    if request.method == 'POST':
        form = DocumentSignForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                document = form.save(commit=False)
                document.ip_address = get_client_ip(request)
                
                if not document.signature_text and not document.signature_image:
                    form.add_error(None, "Forneça uma assinatura (texto ou imagem)")
                    return render(request, 'signer/index.html', {'form': form})
                
                document.save()
                signed_path = process_document(document)
                doc_id = document.id
                success = True
                
                response = FileResponse(open(signed_path, 'rb'), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="documento_assinado_{document.id}.pdf"'
                return response
                
            except Exception as e:
                traceback.print_exc()
                return render(request, 'signer/index.html', {
                    'form': form,
                    'error': f"Erro no processamento: {str(e)}"
                })
    
    form = DocumentSignForm()
    return render(request, 'signer/index.html', {
        'form': form,
        'success': success,
        'doc_id': doc_id
    })
    
def download_document(request, doc_id):
    """Função alternativa para download posterior"""
    try:
        document = SignedDocument.objects.get(id=doc_id)
        
        if not document.signed_file:
            return HttpResponse("Documento não encontrado", status=404)
        
        response = FileResponse(
            open(document.signed_file.path, 'rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="documento_assinado_{document.id}.pdf"'
        return response
    
    except SignedDocument.DoesNotExist:
        return HttpResponse("Documento não encontrado", status=404)
    except Exception as e:
        traceback.print_exc()
        return HttpResponse(f"Erro ao baixar documento: {str(e)}", status=500)
        