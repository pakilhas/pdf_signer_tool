from django.contrib import admin
from .models import SignedDocument

class SignedDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_original_filename',  # Método personalizado
        'signature_position',
        'created_at',
        'ip_address'
    )
    
    list_filter = (
        'created_at',
        'signature_position',
    )
    
    search_fields = (
        'original_file__icontains',
        'signature_text__icontains',
        'ip_address'
    )
    
    readonly_fields = (
        'get_original_filename',
        'created_at',
        'ip_address'
    )
    
    # Método para exibir o nome do arquivo original
    def get_original_filename(self, obj):
        return obj.original_filename
    get_original_filename.short_description = 'Nome do Arquivo'

admin.site.register(SignedDocument, SignedDocumentAdmin)