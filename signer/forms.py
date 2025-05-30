from django import forms
from django.core.exceptions import ValidationError
from .models import SignedDocument



class DocumentSignForm(forms.ModelForm):
    class Meta:
        model = SignedDocument
        fields = ['original_file', 'signature_text']
        widgets = {
            'original_file': forms.FileInput(attrs={
                'accept': '.pdf',
                'onchange': 'previewPDF(this)'
            }),
            'signature_text': forms.TextInput(attrs={
                'placeholder': 'Digite o texto da assinatura...'
            })
        }