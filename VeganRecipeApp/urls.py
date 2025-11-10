from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Include the URLs from our 'recipes' app
    path('', include('goodTastesLike2.urls')),
]

# This is necessary to serve media files (like recipe images)
# during development. This is NOT for production use.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)