from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from .forms import DocumentSignForm
from .models import SignedDocument
from .utils import process_document
import traceback

def get_client_ip(request):
    """Obtém o IP do cliente de forma segura"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')

def home(request):
    if request.method == 'POST':
        form = DocumentSignForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                document = form.save(commit=False)
                document.ip_address = get_client_ip(request)
                document.save()  # Salva primeiro para gerar ID
                
                # Processa o PDF com assinatura fixa
                signed_path = process_document(document)
                
                # Força download imediato
                with open(signed_path, 'rb') as pdf_file:
                    response = HttpResponse(
                        pdf_file.read(),
                        content_type='application/pdf'
                    )
                    response['Content-Disposition'] = f'attachment; filename="documento_assinado_{document.id}.pdf"'
                    return response

            except Exception as e:
                traceback.print_exc()
                return render(request, 'signer/index.html', {
                    'form': form,
                    'error': f"Erro: {str(e)}"
                })
        else:
            return render(request, 'signer/index.html', {'form': form})
    
    # GET: Exibe formulário vazio
    form = DocumentSignForm()
    return render(request, 'signer/index.html', {'form': form})

def download_document(request, doc_id):
    try:
        document = SignedDocument.objects.get(id=doc_id)
        if document.signed_file:
            return FileResponse(
                open(document.signed_file.path, 'rb'),
                content_type='application/pdf',
                filename=f"documento_assinado_{doc_id}.pdf"
            )
        return HttpResponse("Documento não encontrado", status=404)
    
    except SignedDocument.DoesNotExist:
        return HttpResponse("Documento não encontrado", status=404)
    except Exception as e:
        traceback.print_exc()
        return HttpResponse(f"Erro interno: {str(e)}", status=500)