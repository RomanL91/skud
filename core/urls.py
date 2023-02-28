from django.contrib import admin
from django.urls import path, include
from django_api_admin.sites import site
from django_restful_admin import admin as api_admin 

from .api_urls import router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('app_skud/', include(('app_skud.urls', 'app_skud'), namespace='app_skud')),
    path('', include(('app_controller.urls', 'app_controller'), namespace='app_controller')),
    # path('api/v1/drf-auth/', include('rest_framework.urls')),
    # path('api/v1/drf-admin/', site.urls),
    # path('api/v1/', include(router.urls)),
]

from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
