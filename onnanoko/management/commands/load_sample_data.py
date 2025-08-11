from django.core.management.base import BaseCommand
from onnanoko.models import Series, Group, Tag, Character, Image
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
import io
from PIL import Image as PILImage
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Load a small sample dataset for development.'

    def handle(self, *args, **options):
        # Create user
        user, _ = User.objects.get_or_create(username='demo', defaults={'is_staff': True, 'is_superuser': True})
        user.set_password('demo')
        user.save()
        self.stdout.write(self.style.SUCCESS('Demo user created: demo/demo'))

        # Series
        s1, _ = Series.objects.get_or_create(name='Idolmaster', slug='idolmaster')
        s2, _ = Series.objects.get_or_create(name='Love Live', slug='love-live')
        # Groups
        g1, _ = Group.objects.get_or_create(name='765PRO', slug='765pro')
        g2, _ = Group.objects.get_or_create(name='Aqours', slug='aqours')
        # Tags
        t1, _ = Tag.objects.get_or_create(name='idol', slug='idol')
        t2, _ = Tag.objects.get_or_create(name='cute', slug='cute')
        t3, _ = Tag.objects.get_or_create(name='school', slug='school')
        # Characters
        c1, _ = Character.objects.get_or_create(
            name='Haruka Amami', slug='haruka-amami', series=s1, is_2d=True,
            defaults={
                'height_cm': 158, 'weight_kg': 46, 'bust_cm': 83, 'waist_cm': 56, 'hips_cm': 80,
                'description': 'Cheerful idol from 765PRO.',
            })
        c1.groups.set([g1])
        c1.tags.set([t1, t2])
        c2, _ = Character.objects.get_or_create(
            name='Chika Takami', slug='chika-takami', series=s2, is_2d=True,
            defaults={
                'height_cm': 157, 'weight_kg': 45, 'bust_cm': 82, 'waist_cm': 59, 'hips_cm': 83,
                'description': 'Energetic leader of Aqours.',
            })
        c2.groups.set([g2])
        c2.tags.set([t1, t3])
        # Placeholder image
        for i, char in enumerate([c1, c2], 1):
            img = PILImage.new('RGB', (400, 600), (random.randint(100,255), random.randint(100,255), random.randint(100,255)))
            buf = io.BytesIO()
            img.save(buf, format='JPEG')
            buf.seek(0)
            image = Image.objects.create(
                uploader=user,
                description=f"Sample image for {char.name}",
            )
            image.file.save(f'sample_{i}.jpg', ContentFile(buf.read()), save=True)
            image.characters.set([char])
            image.tags.set([t1])
            image.is_approved = True
            image.save()
        self.stdout.write(self.style.SUCCESS('Sample data loaded.'))
