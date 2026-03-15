from django.contrib import admin
from .models import Category, SchoolClass, Subject, Lesson, ContactRequest, VisitorLog, Tag, BlogPost

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'school_class', 'category', 'order', 'is_active')
    list_filter = ('school_class', 'category', 'is_active')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'youtube_id', 'order', 'is_published', 'views_count')
    list_filter = ('is_published', 'subject')
    search_fields = ('title', 'youtube_id')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'email', 'message')
    readonly_fields = ('created_at',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'is_featured', 'created_at')
    list_filter = ('status', 'is_featured', 'category', 'created_at', 'has_math', 'has_chart')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'content', 'excerpt', 'thumbnail')
        }),
        ('Classification', {
            'fields': ('category', 'tags', 'status', 'is_featured')
        }),
        ('Content Features', {
            'fields': ('has_math', 'has_chart', 'has_video', 'has_animation')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'path', 'method', 'timestamp')
    list_filter = ('method', 'timestamp')
    search_fields = ('ip_address', 'path')

    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
