from .models import SiteSetting

def site_settings(request):
    s = SiteSetting.get_solo()
    return {
        'site_settings': s,
    }
