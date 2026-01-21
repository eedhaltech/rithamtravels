from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'views', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views', 'created_at', 'updated_at')
    list_per_page = 25
    
    # Use get_fields instead of fieldsets to avoid context copying issues
    def get_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return ('title', 'slug', 'author', 'is_published', 'excerpt', 'content', 'image', 'views', 'created_at', 'updated_at')
        else:  # Adding new object
            return ('title', 'slug', 'author', 'is_published', 'excerpt', 'content', 'image')
    
    # Override templates to use custom templates that avoid Python 3.14 compatibility issue
    change_list_template = 'admin/blog/blogpost/change_list.html'
    change_form_template = 'admin/blog/blogpost/change_form.html'

