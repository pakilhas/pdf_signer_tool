from django.contrib import admin
from .models import SignedDocument

@admin.register(SignedDocument)
class SignedDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_filename', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('original_filename', 'signature_text')