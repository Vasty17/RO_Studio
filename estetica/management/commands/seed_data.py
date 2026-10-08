from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from estetica.models import Categoria, Servicio


class Command(BaseCommand):
    help = 'Sembrar categorías y los 11 servicios iniciales aprobados de Ro Studio'

    def handle(self, *args, **options):
        # Crear superusuario admin si no existe
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@rostudio.cl', 'admin1234')
            self.stdout.write(self.style.SUCCESS("Superusuario 'admin' (password: admin1234) creado correctamente."))

        categorias_data = [
            {
                'slug': 'unas',
                'nombre': 'Uñas',
                'emoji': '💅',
                'subtitulo': 'Manicura & Pedicura de Autor',
                'orden': 1
            },
            {
                'slug': 'pelo',
                'nombre': 'Pelo',
                'emoji': '💇',
                'subtitulo': 'Estilismo & Alquimia Capilar',
                'orden': 2
            },
            {
                'slug': 'maquillaje',
                'nombre': 'Maquillaje',
                'emoji': '💄',
                'subtitulo': 'Maquillaje de Autor & Gala',
                'orden': 3
            },
        ]

        cat_objs = {}
        for c in categorias_data:
            obj, _ = Categoria.objects.update_or_create(
                slug=c['slug'],
                defaults=c
            )
            cat_objs[c['slug']] = obj

        servicios_data = [
            # Uñas
            {
                'categoria': cat_objs['unas'],
                'nombre': 'Manicure Tradicional',
                'descripcion': 'Tratamiento higiénico de cutículas, limado anatómico, hidratación profunda con aceites botánicos de almendra y esmaltado clásico premium.',
                'precio': 15000,
                'duracion_minutos': 45,
                'badge': 'Disponible Hoy',
                'orden': 1,
            },
            {
                'categoria': cat_objs['unas'],
                'nombre': 'Manicure Permanente',
                'descripcion': 'Esmaltado semipermanente de fijación fotopolimerizada. Brillo de cristal cósmico con nutrición de keratina botánica y duración intacta de 21 días.',
                'precio': 24000,
                'duracion_minutos': 60,
                'badge': 'Pocos cupos hoy',
                'orden': 2,
            },
            {
                'categoria': cat_objs['unas'],
                'nombre': 'Nail Art de Autor',
                'descripcion': 'Diseños personalizados a mano alzada, destellos celestiales, encapsulado floral, aplicaciones de oro líquido y trazos botánicos por artistas residentes.',
                'precio': 32000,
                'duracion_minutos': 75,
                'badge': 'Firma Exclusiva',
                'orden': 3,
            },
            {
                'categoria': cat_objs['unas'],
                'nombre': 'Pedicure Spa Exfoliante',
                'descripcion': 'Inmersión aromática con sales marinas puras, pulido celular, máscara oclusiva de manteca de karité cósmica y masaje podológico relajante.',
                'precio': 28000,
                'duracion_minutos': 60,
                'badge': 'Disponible Hoy',
                'orden': 4,
            },
            # Pelo
            {
                'categoria': cat_objs['pelo'],
                'nombre': 'Corte de Pelo & Asesoría',
                'descripcion': 'Diagnóstico fisionómico y corte arquitectónico adaptado a tus facciones. Incluye lavado botánico bio-activo y secado orgánico con acabado texturizado.',
                'precio': 22000,
                'duracion_minutos': 50,
                'badge': 'Disponible Hoy',
                'orden': 1,
            },
            {
                'categoria': cat_objs['pelo'],
                'nombre': 'Lavado y Peinado / Brushing',
                'descripcion': 'Purificación capilar con masaje craneal y técnica de secado con cepillos de cerdas naturales para volumen fluido o pulido seda impecable.',
                'precio': 18000,
                'duracion_minutos': 40,
                'badge': 'Disponible Hoy',
                'orden': 2,
            },
            {
                'categoria': cat_objs['pelo'],
                'nombre': 'Brushing Glaze & Brillo',
                'descripcion': 'Tratamiento exprés de laminado y sellado con infusión de ácido hialurónico capilar y peinado de pulido espejo con protección térmica estelar.',
                'precio': 25000,
                'duracion_minutos': 50,
                'badge': 'Pocos cupos hoy',
                'orden': 3,
            },
            {
                'categoria': cat_objs['pelo'],
                'nombre': 'Peinado de Fiesta & Eventos',
                'descripcion': 'Recogidos estructurados, semirecogidos etéreos u ondas cósmicas ultra duraderas diseñadas para deslumbrar toda la noche.',
                'precio': 38000,
                'duracion_minutos': 80,
                'badge': 'Disponible Hoy',
                'orden': 4,
            },
            # Maquillaje
            {
                'categoria': cat_objs['maquillaje'],
                'nombre': 'Maquillaje Social de Día',
                'descripcion': 'Piel translúcida tipo "clean star look". Corrección cromática ligera, realce natural de pestañas y labios con tinte satinado para almuerzos o eventos.',
                'precio': 30000,
                'duracion_minutos': 60,
                'badge': 'Disponible Hoy',
                'orden': 1,
            },
            {
                'categoria': cat_objs['maquillaje'],
                'nombre': 'Maquillaje de Fiesta & Noche',
                'descripcion': 'Contouring dimensional galáctico, mirada ahumada de alta definición, fijador de larga duración e instalación de pestañas individuales estelares.',
                'precio': 42000,
                'duracion_minutos': 75,
                'badge': 'Disponible Hoy',
                'orden': 2,
            },
            {
                'categoria': cat_objs['maquillaje'],
                'nombre': 'Maquillaje para Eventos & Novias',
                'descripcion': 'Ritual de preparación con ampolla flash luminosa, base HD resistente a lágrimas y fotografía estelar. Incluye kit exclusivo de retoque Ro Studio.',
                'precio': 55000,
                'duracion_minutos': 90,
                'badge': 'Pocos cupos hoy',
                'orden': 3,
            },
        ]

        for s in servicios_data:
            Servicio.objects.update_or_create(
                nombre=s['nombre'],
                defaults=s
            )

        self.stdout.write(self.style.SUCCESS(f"Se crearon/actualizaron {len(servicios_data)} servicios exitosamente."))
