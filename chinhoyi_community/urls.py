"""
URL configuration for chinhoyi_community project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Core + PWA
    path('', include('core.urls')),
    path('', include('pwa.urls')),

    # Apps
    path('accounts/', include('accounts.urls')),
    path('listings/', include('listings.urls')),
    path('messaging/', include(('messaging.urls', 'messaging'), namespace='messaging')),
    path('dashboard/', include('dashboard.urls')),

    # JWT Auth
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API Endpoints (DRF routers)
    path('api/', include('listings.api_urls')),
    path('api/messaging/', include('messaging.api_urls')),
]

# Serve media files in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
