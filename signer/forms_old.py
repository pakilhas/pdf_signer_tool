from django import forms
from django.core.exceptions import ValidationError
from .models import SignedDocument

class DocumentSignForm(forms.ModelForm):
    class Meta:
        model = SignedDocument
        fields = [
            'original_file',
            'signature_text',
            'signature_position'
        ]
        
        labels = {
            'original_file': 'Documento PDF',
            'signature_text': 'Texto da Assinatura',
            'signature_position': 'Posição no Rodapé'
        }
        
        widgets = {
            'original_file': forms.FileInput(attrs={'accept': '.pdf'}),
            'signature_text': forms.TextInput(attrs={
                'placeholder': 'Digite o texto da assinatura...'
            }),
            'signature_position': forms.Select(attrs={'class': 'form-control'})
        }

    def clean(self):
        cleaned_data = super().clean()
        signature_text = cleaned_data.get('signature_text')
        
        if not signature_text:
            raise ValidationError("O texto da assinatura é obrigatório.")
        
        return cleaned_data