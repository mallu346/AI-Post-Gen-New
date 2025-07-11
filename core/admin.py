from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Post, GeneratedImage, Comment, Like, StylePreset, Feedback

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('bio', 'profile_picture', 'website', 'location', 'birth_date')
        }),
    )

@admin.register(GeneratedImage)
class GeneratedImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'prompt_preview', 'style_preset', 'generation_source', 'is_public', 'created_at')
    list_filter = ('style_preset', 'generation_source', 'is_public', 'created_at', 'user')
    search_fields = ('prompt', 'user__username')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)
    
    def prompt_preview(self, obj):
        return obj.prompt[:50] + '...' if len(obj.prompt) > 50 else obj.prompt
    prompt_preview.short_description = 'Prompt'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title_preview', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at', 'user')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    def title_preview(self, obj):
        return obj.title[:30] + '...' if len(obj.title) > 30 else obj.title
    title_preview.short_description = 'Title'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'content_preview', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('content', 'user__username', 'post__title')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    list_filter = ('created_at', 'user')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)

@admin.register(StylePreset)
class StylePresetAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_preview', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description'

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'rating', 'message_preview', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('message', 'user__username')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'

# Register the CustomUser with our custom admin
admin.site.register(CustomUser, CustomUserAdmin)

# Customize admin site headers
admin.site.site_header = "AI Social Media Platform Admin"
admin.site.site_title = "AI Social Platform"
admin.site.index_title = "Welcome to AI Social Media Platform Administration"
