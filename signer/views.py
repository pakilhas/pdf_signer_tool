from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from .forms import DocumentSignForm
from .utils import sign_pdf
import os
from django.conf import settings
import traceback

def home(request):
    try:
        if request.method == 'POST':
            form = DocumentSignForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    # Verificação de assinatura
                    if not any([form.cleaned_data.get('signature_text'), 'signature_image' in request.FILES]):
                        return render(request, 'signer/index.html', {
                            'form': form,
                            'error': "Por favor, forneça uma assinatura"
                        })
                    
                    # Processamento do documento
                    signed_path = sign_pdf(
                        pdf_file=request.FILES['document'],
                        signature_text=form.cleaned_data.get('signature_text'),
                        signature_image=request.FILES.get('signature_image')
                    )
                    
                    # Resposta com o arquivo
                    response = FileResponse(
                        open(signed_path, 'rb'),
                        content_type='application/pdf'
                    )
                    response['Content-Disposition'] = 'attachment; filename="documento_assinado.pdf"'
                    
                    # Limpeza após download
                    def cleanup():
                        if os.path.exists(signed_path):
                            os.remove(signed_path)
                    
                    response._resource_closers.append(cleanup)
                    return response
                
                except Exception as e:
                    traceback.print_exc()
                    return render(request, 'signer/index.html', {
                        'form': form,
                        'error': f"Erro no processamento: {str(e)}"
                    })
        
        # GET request
        form = DocumentSignForm()
        return render(request, 'signer/index.html', {'form': form})
    
    except Exception as e:
        traceback.print_exc()
        return HttpResponse(f"Erro interno: {str(e)}", status=500)