from django.conf import settings

from .models import SiteBranding, WebsiteImage


def site_assets(request):
    branding = SiteBranding.objects.order_by('-updated_at').first()
    images = WebsiteImage.objects.filter(is_active=True)
    return {
        'site_branding': branding,
        'website_images': images,
        'default_logo_url': f'{settings.MEDIA_URL}logo.png',
    }
