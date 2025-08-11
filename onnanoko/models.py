from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.utils import timezone

User = get_user_model()

class Series(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [models.Index(fields=['slug'])]

class Group(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [models.Index(fields=['slug'])]

class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [models.Index(fields=['slug'])]

class Character(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, unique=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    bust_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    waist_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    hips_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_2d = models.BooleanField(default=True)
    series = models.ForeignKey(Series, null=True, blank=True, on_delete=models.SET_NULL, related_name='characters')
    groups = models.ManyToManyField(Group, blank=True, related_name='characters')
    tags = models.ManyToManyField(Tag, blank=True, related_name='characters')
    description = models.TextField(blank=True)
    primary_image = models.ImageField(upload_to='characters/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.age and self.birth_date:
            raise ValueError('Provide either age or birth_date, not both.')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [models.Index(fields=['slug'])]
        unique_together = ('name', 'series')

class Image(models.Model):
    file = models.ImageField(upload_to='images/')
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_images')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    characters = models.ManyToManyField(Character, related_name='images', blank=True)
    tags = models.ManyToManyField(Tag, related_name='images', blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    illustrator = models.CharField(max_length=128, blank=True, help_text="Name of the artist/illustrator")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.file and (not self.width or not self.height):
            from PIL import Image as PILImage
            import os
            img_path = self.file.path
            with PILImage.open(img_path) as img:
                self.width, self.height = img.size
            super().save(update_fields=['width', 'height'])

    def __str__(self):
        return f"Image {self.id} by {self.uploader}"

class SiteSetting(models.Model):
    allow_self_registration = models.BooleanField(default=True)

    def __str__(self) -> str:
        return "Site Settings"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
