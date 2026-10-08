import random
import string
from django.db import models


def generar_codigo_reserva():
    numero = ''.join(random.choices(string.digits, k=4))
    return f"RO-{numero}"


class Categoria(models.Model):
    SLUGS = [
        ('unas', 'Uñas'),
        ('pelo', 'Pelo'),
        ('maquillaje', 'Maquillaje'),
    ]
    slug = models.SlugField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    emoji = models.CharField(max_length=10, default='✦')
    subtitulo = models.CharField(max_length=200, blank=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return f"{self.emoji} {self.nombre}"


class Servicio(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='servicios')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.PositiveIntegerField(help_text="Precio en CLP (ej. 24000)")
    duracion_minutos = models.PositiveIntegerField(default=60, help_text="Duración en minutos")
    badge = models.CharField(max_length=100, default='Disponible Hoy', blank=True)
    imagen_url = models.URLField(max_length=500, blank=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['categoria__orden', 'orden', 'nombre']
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'

    def __str__(self):
        return f"{self.nombre} (${self.precio:,})".replace(',', '.')

    @property
    def precio_formateado(self):
        return f"${self.precio:,}".replace(',', '.')

    @property
    def duracion_texto(self):
        return f"{self.duracion_minutos} min"


class Reserva(models.Model):
    ESTADOS = [
        ('confirmada', 'Confirmada'),
        ('reprogramada', 'Reprogramada'),
        ('cancelada', 'Cancelada'),
    ]

    MODALIDADES = [
        ('domicilio', 'A Domicilio'),
        ('estudio_privado', 'Estudio Privado de la Especialista'),
    ]

    codigo = models.CharField(max_length=20, unique=True, default=generar_codigo_reserva, editable=False)
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT, related_name='reservas')
    fecha = models.DateField(help_text="Fecha de la cita")
    hora = models.CharField(max_length=10, help_text="Hora en formato HH:MM (ej. 11:30)")
    modalidad = models.CharField(max_length=50, choices=MODALIDADES, default='domicilio')
    direccion = models.CharField(max_length=300, blank=True, help_text="Dirección para atención a domicilio")
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=50)
    email = models.EmailField()
    comentario = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='confirmada')
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha', 'hora']
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        constraints = [
            # Restricción UNIQUE para evitar que dos clientes reserven el mismo horario en la misma fecha y servicio
            models.UniqueConstraint(
                fields=['fecha', 'hora', 'servicio'],
                condition=models.Q(estado__in=['confirmada', 'reprogramada']),
                name='unique_reserva_activa_fecha_hora_servicio'
            )
        ]

    def __str__(self):
        return f"[{self.codigo}] {self.nombre} {self.apellido} - {self.servicio.nombre} ({self.fecha} {self.hora})"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}".strip()
