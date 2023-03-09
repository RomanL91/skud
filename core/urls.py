from django.contrib import admin
from django.urls import path, include
from django_api_admin.sites import site


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('app_controller.urls', 'app_controller'), namespace='app_controller')),
    path('monitor_events/', include(('app_skud.urls', 'app_skud'), namespace='app_skud')),
]


from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
