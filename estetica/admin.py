from django.contrib import admin
from .models import Categoria, Servicio, Reserva


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'emoji', 'orden')
    prepopulated_fields = {'slug': ('nombre',)}
    ordering = ('orden',)


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio_formateado', 'duracion_texto', 'badge', 'activo', 'orden')
    list_filter = ('categoria', 'activo')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('activo', 'orden')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre_completo', 'servicio', 'fecha', 'hora', 'modalidad', 'telefono', 'estado', 'creada_en')
    list_filter = ('estado', 'fecha', 'modalidad', 'servicio__categoria')
    search_fields = ('codigo', 'nombre', 'apellido', 'email', 'telefono')
    readonly_fields = ('codigo', 'creada_en', 'actualizada_en')
