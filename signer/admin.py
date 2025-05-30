from django.contrib import admin
from .models import SignedDocument

class SignedDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_original_filename',  # Método personalizado
        'get_signature_info',     # Assinatura resumida
        'get_watermark_info',     # Marca d'água resumida
        'created_at',
        'ip_address'
    )
    
    list_filter = (
        'created_at',
        'signature_position',
    )
    
    search_fields = (
        'original_file',
        'signature_text',
        'ip_address'
    )
    
    readonly_fields = (
        'get_original_filename',
        'created_at',
        'ip_address',
        'get_signature_preview',
        'get_watermark_preview'
    )
    
    fieldsets = (
        ('Documento PDF', {
            'fields': ('original_file', 'signed_file', 'get_original_filename')
        }),
        ('Marca D\'Água', {
            'fields': ('watermark_image', 'watermark_opacity', 'get_watermark_preview')
        }),
        ('Assinatura', {
            'fields': (
                'signature_text', 
                'signature_image', 
                'signature_position',
                'get_signature_preview'
            )
        }),
        ('Metadados', {
            'fields': ('ip_address', 'created_at')
        }),
    )
    
    # 1. Método para exibir o nome do arquivo original
    def get_original_filename(self, obj):
        return obj.original_filename
    get_original_filename.short_description = 'Nome do Arquivo'
    
    # 2. Método para mostrar informações resumidas da assinatura
    def get_signature_info(self, obj):
        if obj.signature_text and obj.signature_image:
            return f"Texto + Imagem ({obj.signature_position})"
        elif obj.signature_text:
            return f"Texto: {obj.signature_text[:20]}... ({obj.signature_position})"
        elif obj.signature_image:
            return f"Imagem ({obj.signature_position})"
        return "Sem assinatura"
    get_signature_info.short_description = 'Assinatura'
    
    # 3. Método para mostrar informações da marca d'água
    def get_watermark_info(self, obj):
        if obj.watermark_image:
            return f"Imagem (Opacidade: {obj.watermark_opacity})"
        return "Sem marca d'água"
    get_watermark_info.short_description = 'Marca D\'Água'
    
    # 4. Pré-visualização da assinatura (somente leitura)
    def get_signature_preview(self, obj):
        if obj.signature_image:
            return f'<img src="{obj.signature_image.url}" style="max-height: 100px; background-color: #f0f0f0; padding: 5px; border: 1px solid #ddd;">'
        return "Nenhuma imagem de assinatura carregada"
    get_signature_preview.short_description = 'Pré-visualização'
    get_signature_preview.allow_tags = True
    
    # 5. Pré-visualização da marca d'água (somente leitura)
    def get_watermark_preview(self, obj):
        if obj.watermark_image:
            return f'<img src="{obj.watermark_image.url}" style="max-height: 100px; background-color: #f0f0f0; padding: 5px; border: 1px solid #ddd; opacity: {obj.watermark_opacity};">'
        return "Nenhuma marca d'água carregada"
    get_watermark_preview.short_description = 'Visualização'
    get_watermark_preview.allow_tags = True

admin.site.register(SignedDocument, SignedDocumentAdmin)