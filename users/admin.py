from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    # List display
    list_display = ['username', 'email', 'full_name', 'phone_number', 'show_avatar', 'date_joined', 'user_status', 'user_role']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    
    readonly_fields = [
        'username', 'email', 'first_name', 'last_name', 
        'phone_number', 'address', 'city', 'postal_code', 
        'date_of_birth', 'bio', 'profile_picture',
        'date_joined', 'last_login', 'show_avatar_large'
    ]
    
    # HAPUS kemampuan ADD USER dari admin
    def has_add_permission(self, request):
        return False
    
    # BATASI kemampuan EDIT
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [
                'username', 'email', 'first_name', 'last_name',
                'phone_number', 'address', 'city', 'postal_code',
                'date_of_birth', 'bio', 'profile_picture',
                'date_joined', 'last_login', 'show_avatar_large'
            ]
        return self.readonly_fields
    
    # Fieldsets
    fieldsets = (
        ('👤 Informasi User (Read-Only)', {
            'fields': ('show_avatar_large', 'username', 'email')
        }),
        ('📝 Data Pribadi (Read-Only)', {
            'fields': ('first_name', 'last_name', 'phone_number', 'date_of_birth', 'bio')
        }),
        ('📍 Alamat (Read-Only)', {
            'fields': ('address', 'city', 'postal_code')
        }),
        ('⚙️ Management (Dapat Diubah)', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'description': 'Hanya bagian ini yang bisa diubah oleh admin'
        }),
        ('📅 Informasi Waktu', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    # Custom display methods
    def show_avatar(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />',
                obj.profile_picture.url
            )
        return format_html(
            '<img src="/static/img/default-avatar.png" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />'
        )
    show_avatar.short_description = 'Avatar'
    
    def show_avatar_large(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="150" height="150" style="border-radius: 10px; object-fit: cover;" />',
                obj.profile_picture.url
            )
        return format_html(
            '<img src="/static/img/default-avatar.png" width="150" height="150" style="border-radius: 10px; object-fit: cover;" />'
        )
    show_avatar_large.short_description = 'Foto Profil'
    
    def full_name(self, obj):
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return "-"
    full_name.short_description = 'Nama Lengkap'
    
    def user_status(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Aktif</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Nonaktif</span>'
        )
    user_status.short_description = 'Status'
    
    def user_role(self, obj):
        if obj.is_superuser:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">SUPERUSER</span>'
            )
        elif obj.is_staff:
            return format_html(
                '<span style="background: #ffc107; color: black; padding: 3px 10px; border-radius: 3px; font-size: 11px;">STAFF</span>'
            )
        return format_html(
            '<span style="background: #28a745; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">USER</span>'
        )
    user_role.short_description = 'Role'