from django.contrib import admin
from .models import Series, Group, Tag, Character, Image, SiteSetting

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]
    list_display = ("name", "slug")

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]
    list_display = ("name", "slug")

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]
    list_display = ("name", "slug")

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "description"]
    list_display = ("name", "series", "is_2d", "created_at")
    list_filter = ("is_2d", "series", "groups", "tags")
    filter_horizontal = ("groups", "tags")

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    search_fields = ["uploader__username", "description", "illustrator"]
    list_display = ("id", "uploader", "illustrator", "uploaded_at", "is_approved")
    list_filter = ("is_approved", "uploaded_at", "tags")
    filter_horizontal = ("characters", "tags")

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("allow_self_registration",)
