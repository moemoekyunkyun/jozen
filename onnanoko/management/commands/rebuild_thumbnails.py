from django.core.management.base import BaseCommand
from onnanoko.models import Image
from PIL import Image as PILImage

class Command(BaseCommand):
    help = 'Rebuild thumbnails and update width/height for all images.'

    def handle(self, *args, **options):
        count = 0
        for img in Image.objects.all():
            try:
                pil_img = PILImage.open(img.file.path)
                img.width, img.height = pil_img.size
                img.save(update_fields=['width', 'height'])
                self.stdout.write(self.style.SUCCESS(f'Rebuilt: {img.file.name}'))
                count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error with {img.file.name}: {e}'))
        self.stdout.write(self.style.SUCCESS(f'Done. {count} images processed.'))
