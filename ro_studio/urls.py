from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Incluir las URLs de la aplicación estetica
    path('', include('estetica.urls')),
    # Django admin estándar en /django-admin/ o /admin/
    path('django-admin/', admin.site.urls),
]
