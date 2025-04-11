from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class SignedDocument(models.Model):
    # Informações do documento original
    original_file = models.FileField(
        upload_to='documents/original/%Y/%m/%d/',
        verbose_name='Documento Original'
    )
    original_filename = models.CharField(
        max_length=255,
        editable=False
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
    watermark_position = models.CharField(
        max_length=20,
        choices=[
            ('center', 'Centro'),
            ('topleft', 'Canto Superior Esquerdo'),
            ('topright', 'Canto Superior Direito'),
            ('bottomleft', 'Canto Inferior Esquerdo'),
            ('bottomright', 'Canto Inferior Direito')
        ],
        default='center',
        verbose_name='Posição da Marca D\'Água'
    )
    
    # Informações de assinatura
    signature_text = models.CharField(
        max_length=255,
        verbose_name='Texto da Assinatura'
    )
    signature_image = models.ImageField(
        upload_to='signatures/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name='Imagem da Assinatura'
    )
    
    # Documento processado
    signed_file = models.FileField(
        upload_to='documents/signed/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name='Documento Assinado'
    )
    
    # Metadados
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Endereço IP'
    )
    
    # Status do processamento
    PROCESSING_STATUS = [
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou')
    ]
    status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS,
        default='pending',
        verbose_name='Status'
    )
    
    class Meta:
        verbose_name = 'Documento Assinado'
        verbose_name_plural = 'Documentos Assinados'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Documento #{self.id} - {self.original_filename}"
    
    def save(self, *args, **kwargs):
        # Salva o nome original do arquivo
        if self.original_file and not self.original_filename:
            self.original_filename = self.original_file.name
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Exclui os arquivos físicos quando o modelo é deletado"""
        storage, path = self.original_file.storage, self.original_file.path
        storage.delete(path)
        if self.signed_file:
            storage, path = self.signed_file.storage, self.signed_file.path
            storage.delete(path)
        super().delete(*args, **kwargs)