from django.contrib import admin
from django.urls import path, re_path, include
from django_api_admin.sites import site

from app_skud.view import MonitorEventsApiView, PerimetrMonitorApiView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('app_controller.urls', 'app_controller'), namespace='app_controller')),
    path('app_skud/', include(('app_skud.urls', 'app_skud'), namespace='app_skud')),
    re_path(r'api/v1/monitors/(?P<pk_checkpoint>\d+)$', MonitorEventsApiView.as_view()),
    re_path(r'api/v1/perimetr/(?P<pk_checkpoint>\d+)$', PerimetrMonitorApiView.as_view()),
]


from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
