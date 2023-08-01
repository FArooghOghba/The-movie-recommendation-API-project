from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path(route="schema/", view=SpectacularAPIView.as_view(api_version="v1"), name="schema"),
    path(route="", view=SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path(route="redoc/", view=SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path(route='admin/', view=admin.site.urls),
    path(route='api/', view=include(('movie_recommendation_api.api.urls', 'api'))),
]


if settings.DEBUG:
    urlpatterns.append(path(route="__debug__/", view=include("debug_toolbar.urls")))
    urlpatterns.append(path(route='api-auth/', view=include('rest_framework.urls')))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
