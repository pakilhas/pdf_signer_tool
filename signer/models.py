from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class SignedDocument(models.Model):
    POSITION_CHOICES = [
        ('left', 'Esquerda'),
        ('center', 'Centro'),
        ('right', 'Direita'),
    ]

    original_file = models.FileField(
        upload_to='documents/original/%Y/%m/%d/',
        verbose_name='Documento Original',
        help_text="Selecione o arquivo PDF para assinar"
    )

    # Configurações da marca d'água
    watermark_image = models.ImageField(
        upload_to='watermarks/%Y/%m/%d/',
        verbose_name='Imagem de Marca D\'Água'
    )
    watermark_opacity = models.FloatField(
        default=0.3,
        validators=[MinValueValidator(0.1), MaxValueValidator(0.9)],
        verbose_name='Transparência da Marca D\'Água'
    )

    # Configurações da assinatura
    signature_text = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Texto da Assinatura'
    )
    signature_image = models.ImageField(
        upload_to='signatures/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name='Imagem da Assinatura'
    )
    signature_position = models.CharField(
        max_length=10,
        choices=POSITION_CHOICES,
        default='left',
        verbose_name='Posição no Rodapé'
    )

    # Metadados
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Endereço IP'
    )
    
    # Documento processado
    signed_file = models.FileField(
        upload_to='documents/signed/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name='Documento Assinado'
    )

    def __str__(self):
        return f"Documento #{self.id} - {self.original_filename}"

    @property
    def original_filename(self):
        return self.original_file.name.split('/')[-1]
    
  
    # Novos campos para coordenadas
    signature_x = models.FloatField(null=True, blank=True)
    signature_y = models.FloatField(null=True, blank=True)
    signature_page = models.PositiveIntegerField(
        default=1,
        verbose_name='Página da Assinatura'
    )

    signature_mode = models.CharField(
        max_length=10,
        choices=[('auto', 'Automático'), ('manual', 'Manual')],
        default='manual'
    )

    def __str__(self):
        return f"Documento #{self.id}"
    
    
    
    signature_mode = models.CharField(
        max_length=10,
        choices=[('auto', 'Automático'), ('manual', 'Manual')],
        default='manual'
    )