from django import forms
from .models import SignedDocument

class DocumentSignForm(forms.ModelForm):
    watermark_opacity = forms.FloatField(
        label='Transparência da Marca D\'Água',
        required=False,
        initial=0.3,
        min_value=0.1,
        max_value=0.9,
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'min': '0.1',
            'max': '0.9',
            'step': '0.1',
            'class': 'opacity-slider'
        }),
        help_text="Ajuste a transparência (0.1 = transparente, 0.9 = mais visível)"
    )
    
    signature_image = forms.FileField(
        label='Imagem da Assinatura (opcional)',
        required=False,
        widget=forms.FileInput(attrs={
            'accept': '.png,.jpg,.jpeg',
            'class': 'signature-image'
        }),
        help_text="Imagem de assinatura escaneada"
    )

    class Meta:
        model = SignedDocument
        fields = [
            'original_file',
            'watermark_image',
            'watermark_opacity',
            'signature_text',
            'signature_image',
            'signature_position'  # Agora controla ambos
        ]
        labels = {
            'signature_position': 'Posição no Rodapé'
        }
        
        widgets = {
            'original_file': forms.FileInput(attrs={'accept': '.pdf'}),
            'watermark_image': forms.FileInput(attrs={'accept': '.png,.jpg,.jpeg'}),
            'signature_text': forms.TextInput(attrs={
                'placeholder': 'Digite o texto da assinatura...'
            }),
            'watermark_position': forms.Select(attrs={'class': 'form-control'}),
            'signature_position': forms.Select(attrs={'class': 'form-control'})
        }
        labels = {
            'original_file': 'Documento PDF',
            'watermark_image': 'Imagem da Marca D\'Água',
            'signature_text': 'Texto da Assinatura',
            'watermark_position': 'Posição da Marca D\'Água',
            'signature_position': 'Posição da Assinatura'
        }

    def clean_watermark_opacity(self):
        opacity = self.cleaned_data.get('watermark_opacity', 0.3)
        return max(0.1, min(0.9, float(opacity)))