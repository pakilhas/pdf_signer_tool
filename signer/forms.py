from django import forms

class DocumentSignForm(forms.Form):
    document = forms.FileField(
        label='Selecione o PDF',
        widget=forms.FileInput(attrs={'accept': '.pdf'}),
        help_text="Selecione o documento PDF que deseja assinar"
    )
    watermark_image = forms.FileField(
        label='Imagem para Marca D\'Água',
        required=True,
        widget=forms.FileInput(attrs={
            'accept': '.png,.jpg,.jpeg',
            'class': 'watermark-input'
        }),
        help_text="Imagem que será usada como fundo semi-transparente"
    )
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
        help_text="Ajuste a transparência da marca d'água (0.1 = quase transparente, 0.9 = mais visível)"
    )
    signature_text = forms.CharField(
        label='Texto da Assinatura',
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ex: Assinado digitalmente por [Seu Nome] em [Data]',
            'class': 'signature-text'
        }),
        help_text="Texto que aparecerá sobre o documento"
    )
    signature_image = forms.FileField(
        label='Imagem da Assinatura (opcional)',
        required=False,
        widget=forms.FileInput(attrs={
            'accept': '.png,.jpg,.jpeg',
            'class': 'signature-image'
        }),
        help_text="Caso queira incluir uma imagem de assinatura escaneada"
    )

    def clean_watermark_opacity(self):
        opacity = self.cleaned_data.get('watermark_opacity', 0.3)
        return max(0.1, min(0.9, float(opacity)))  # Garante que está entre 0.1 e 0.9