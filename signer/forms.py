from django import forms

class DocumentSignForm(forms.Form):
    document = forms.FileField(
        label='Selecione o PDF',
        widget=forms.FileInput(attrs={'accept': '.pdf'})
    )
    signature_text = forms.CharField(
        label='Texto da Assinatura (opcional)',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ex: Assinado digitalmente em 14/12/2025'
        })
    )
    signature_image = forms.FileField(
        label='Imagem da Assinatura (opcional)',
        required=False,
        widget=forms.FileInput(attrs={'accept': '.png,.jpg,.jpeg'})
    )