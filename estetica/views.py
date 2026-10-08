from datetime import date, datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from .models import Categoria, Servicio, Reserva


HORARIOS_ESTANDAR = [
    '10:00',
    '11:30',
    '12:30',
    '14:00',
    '16:30',
    '18:00',
]


def inicio(request):
    """Página de inicio (/)"""
    servicios_destacados = Servicio.objects.filter(activo=True)[:3]
    categorias = Categoria.objects.all().prefetch_related('servicios')

    # Precios mínimos dinámicos para las 3 tarjetas principales según la base de datos
    min_unas = Servicio.objects.filter(categoria__slug='unas', activo=True).order_by('precio').first()
    min_pelo = Servicio.objects.filter(categoria__slug='pelo', activo=True).order_by('precio').first()
    min_maq = Servicio.objects.filter(categoria__slug='maquillaje', activo=True).order_by('precio').first()

    return render(request, 'inicio.html', {
        'pagina_actual': 'inicio',
        'categorias': categorias,
        'servicios_destacados': servicios_destacados,
        'precio_desde_unas': min_unas.precio_formateado if min_unas else '$15.000',
        'precio_desde_pelo': min_pelo.precio_formateado if min_pelo else '$18.000',
        'precio_desde_maq': min_maq.precio_formateado if min_maq else '$30.000',
    })


def servicios_view(request):
    """Página de Servicios y Tarifas (/servicios/)"""
    categoria_slug = request.GET.get('categoria', 'all')
    busqueda = request.GET.get('q', '').strip()

    servicios = Servicio.objects.filter(activo=True)
    if categoria_slug != 'all':
        servicios = servicios.filter(categoria__slug=categoria_slug)
    if busqueda:
        servicios = servicios.filter(nombre__icontains=busqueda)

    categorias = Categoria.objects.all().prefetch_related('servicios')
    total_servicios = Servicio.objects.filter(activo=True).count()

    return render(request, 'servicios.html', {
        'pagina_actual': 'servicios',
        'categorias': categorias,
        'servicios': servicios,
        'total_servicios': total_servicios,
        'categoria_seleccionada': categoria_slug,
        'busqueda': busqueda,
    })


@csrf_exempt
def reserva_view(request):
    """Página de Reserva de Cita (/reserva/) con protección contra duplicados"""
    servicios = Servicio.objects.filter(activo=True)
    
    # Servicio preseleccionado
    servicio_id = request.GET.get('servicio_id')
    servicio_seleccionado = None
    if servicio_id:
        servicio_seleccionado = servicios.filter(id=servicio_id).first()
    if not servicio_seleccionado:
        # Default a Manicure Permanente si existe, o el primero
        servicio_seleccionado = servicios.filter(nombre__icontains='Permanente').first() or servicios.first()

    # Fecha por defecto: próximo día hábil o el especificado
    fecha_str = request.GET.get('fecha')
    if fecha_str:
        try:
            fecha_seleccionada = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha_seleccionada = date.today() + timedelta(days=1)
    else:
        fecha_seleccionada = date.today() + timedelta(days=1)

    hora_seleccionada = request.GET.get('hora', '11:30')

    error_mensaje = None

    if request.method == 'POST':
        servicio_post_id = request.POST.get('servicio_id')
        fecha_post_str = request.POST.get('fecha')
        hora_post = request.POST.get('hora')
        modalidad = request.POST.get('modalidad', 'domicilio')
        direccion = request.POST.get('direccion', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        email = request.POST.get('email', '').strip()
        comentario = request.POST.get('comentario', '').strip()

        try:
            servicio_obj = Servicio.objects.get(id=servicio_post_id, activo=True)
            fecha_obj = datetime.strptime(fecha_post_str, '%Y-%m-%d').date()

            # Transacción atómica con verificación estricta para evitar doble reserva concurrente
            with transaction.atomic():
                # Verificar si ya existe una reserva activa para este mismo servicio, fecha y hora
                conflicto = Reserva.objects.select_for_update().filter(
                    servicio=servicio_obj,
                    fecha=fecha_obj,
                    hora=hora_post,
                    estado__in=['confirmada', 'reprogramada']
                ).exists()

                if conflicto:
                    error_mensaje = "Lo sentimos, este horario acaba de ser reservado. Por favor selecciona otro horario."
                else:
                    nueva_reserva = Reserva(
                        servicio=servicio_obj,
                        fecha=fecha_obj,
                        hora=hora_post,
                        modalidad=modalidad,
                        direccion=direccion,
                        nombre=nombre,
                        apellido=apellido,
                        telefono=telefono,
                        email=email,
                        comentario=comentario,
                        estado='confirmada'
                    )
                    nueva_reserva.save()
                    # Redirigir a la página de confirmación independiente con URL real
                    return redirect(f"{reverse('reserva_confirmada')}?codigo={nueva_reserva.codigo}")

        except Servicio.DoesNotExist:
            error_mensaje = "El servicio seleccionado no está disponible."
        except IntegrityError:
            # Captura de colisión a nivel de restricción UNIQUE en la base de datos
            error_mensaje = "Lo sentimos, este horario acaba de ser reservado. Por favor selecciona otro horario."
        except Exception as e:
            error_mensaje = f"Ocurrió un error al procesar tu reserva: {str(e)}"

    # Consultar horas ocupadas para la fecha y servicio en la base de datos
    horas_ocupadas = list(Reserva.objects.filter(
        servicio=servicio_seleccionado,
        fecha=fecha_seleccionada,
        estado__in=['confirmada', 'reprogramada']
    ).values_list('hora', flat=True)) if servicio_seleccionado else []

    # Lista de horas con estado
    bloques_horarios = []
    for h in HORARIOS_ESTANDAR:
        bloques_horarios.append({
            'hora': h,
            'ocupado': h in horas_ocupadas,
            'seleccionado': (h == hora_seleccionada and h not in horas_ocupadas),
        })

    return render(request, 'reserva.html', {
        'pagina_actual': 'reserva',
        'servicios': servicios,
        'servicio_seleccionado': servicio_seleccionado,
        'fecha_seleccionada': fecha_seleccionada,
        'fecha_seleccionada_str': fecha_seleccionada.strftime('%Y-%m-%d'),
        'hora_seleccionada': hora_seleccionada,
        'bloques_horarios': bloques_horarios,
        'error_mensaje': error_mensaje,
    })


def reserva_confirmada_view(request):
    """Página de confirmación de reserva independiente (/reserva/confirmada/)"""
    codigo = request.GET.get('codigo')
    reserva = None
    if codigo:
        reserva = Reserva.objects.filter(codigo=codigo).select_related('servicio', 'servicio__categoria').first()

    return render(request, 'reserva_confirmada.html', {
        'pagina_actual': 'reserva_confirmada',
        'reserva': reserva,
        'codigo': codigo,
    })


def contacto_view(request):
    """Página de Información y Contacto (/contacto/)"""
    resultado_busqueda = None
    error_busqueda = None
    
    codigo_buscar = request.GET.get('codigo_buscar', '').strip().upper()
    if codigo_buscar:
        reserva = Reserva.objects.filter(codigo=codigo_buscar).select_related('servicio').first()
        if reserva:
            resultado_busqueda = reserva
        else:
            error_busqueda = f"No se encontró ninguna cita con el código {codigo_buscar}."

    return render(request, 'contacto.html', {
        'pagina_actual': 'contacto',
        'resultado_busqueda': resultado_busqueda,
        'error_busqueda': error_busqueda,
        'codigo_buscar': codigo_buscar,
    })


def api_disponibilidad(request):
    """API para consultar disponibilidad de horarios en tiempo real"""
    fecha_str = request.GET.get('fecha')
    servicio_id = request.GET.get('servicio_id')

    if not fecha_str or not servicio_id:
        return JsonResponse({'error': 'Faltan parámetros'}, status=400)

    try:
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        horas_ocupadas = list(Reserva.objects.filter(
            servicio_id=servicio_id,
            fecha=fecha_obj,
            estado__in=['confirmada', 'reprogramada']
        ).values_list('hora', flat=True))

        disponibilidad = []
        for h in HORARIOS_ESTANDAR:
            disponibilidad.append({
                'hora': h,
                'disponible': h not in horas_ocupadas
            })

        return JsonResponse({'disponibilidad': disponibilidad})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==========================================
# RUTAS DE ADMINISTRACIÓN PROTEGIDAS
# ==========================================

@csrf_exempt
def admin_login_view(request):
    """Login para administración protegida (/admin/login/)"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    error = None
    if request.method == 'POST':
        usuario = request.POST.get('username')
        clave = request.POST.get('password')
        user = authenticate(request, username=usuario, password=clave)
        if user is not None and user.is_staff:
            auth_login(request, user)
            next_url = request.GET.get('next') or reverse('admin_dashboard')
            return redirect(next_url)
        else:
            error = "Credenciales incorrectas o usuario sin permisos de administración."

    return render(request, 'admin/login.html', {'error': error})


def admin_logout_view(request):
    """Cerrar sesión de administrador"""
    auth_logout(request)
    return redirect('admin_login')


@login_required(login_url='/admin/login/')
def admin_dashboard_view(request):
    """Dashboard de administración (/admin/dashboard/)"""
    if not request.user.is_staff:
        return redirect('admin_login')

    total_reservas = Reserva.objects.count()
    reservas_hoy = Reserva.objects.filter(fecha=date.today(), estado='confirmada').count()
    reservas_pendientes = Reserva.objects.filter(estado='confirmada').count()
    ultimas_reservas = Reserva.objects.select_related('servicio').order_by('-creada_en')[:10]
    total_servicios = Servicio.objects.count()

    return render(request, 'admin/dashboard.html', {
        'total_reservas': total_reservas,
        'reservas_hoy': reservas_hoy,
        'reservas_pendientes': reservas_pendientes,
        'ultimas_reservas': ultimas_reservas,
        'total_servicios': total_servicios,
    })


@csrf_exempt
@login_required(login_url='/admin/login/')
def admin_reservas_view(request):
    """Gestión de reservas (/admin/reservas/)"""
    if not request.user.is_staff:
        return redirect('admin_login')

    # Cambio de estado de reserva
    if request.method == 'POST':
        reserva_id = request.POST.get('reserva_id')
        nuevo_estado = request.POST.get('nuevo_estado')
        if reserva_id and nuevo_estado:
            r = get_object_or_404(Reserva, id=reserva_id)
            r.estado = nuevo_estado
            r.save()
            messages.success(request, f"Reserva {r.codigo} actualizada a {nuevo_estado}.")
            return redirect('admin_reservas')

    reservas = Reserva.objects.select_related('servicio').order_by('-fecha', 'hora')
    return render(request, 'admin/reservas.html', {'reservas': reservas})


@csrf_exempt
@login_required(login_url='/admin/login/')
def admin_servicios_view(request):
    """Gestión y edición completa de servicios (/admin/servicios/)"""
    if not request.user.is_staff:
        return redirect('admin_login')

    if request.method == 'POST':
        action = request.POST.get('action')
        servicio_id = request.POST.get('servicio_id')

        if action == 'guardar':
            nombre = request.POST.get('nombre', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            precio_raw = request.POST.get('precio', '0').replace('.', '').replace('$', '').strip()
            duracion_raw = request.POST.get('duracion_minutos', '60').strip()
            badge = request.POST.get('badge', '').strip()
            categoria_id = request.POST.get('categoria_id')
            activo = request.POST.get('activo') in ['on', 'true', '1']

            try:
                precio = max(0, int(precio_raw))
            except ValueError:
                precio = 15000

            try:
                duracion = max(5, int(duracion_raw))
            except ValueError:
                duracion = 60

            if servicio_id:
                s = get_object_or_404(Servicio, id=servicio_id)
                s.nombre = nombre
                s.descripcion = descripcion
                s.precio = precio
                s.duracion_minutos = duracion
                s.badge = badge
                s.activo = activo
                if categoria_id:
                    s.categoria_id = categoria_id
                s.save()
                messages.success(request, f"Servicio '{s.nombre}' actualizado correctamente (Tarifa: {s.precio_formateado}, Duración: {s.duracion_texto}).")
            else:
                cat = get_object_or_404(Categoria, id=categoria_id)
                s = Servicio.objects.create(
                    categoria=cat,
                    nombre=nombre,
                    descripcion=descripcion,
                    precio=precio,
                    duracion_minutos=duracion,
                    badge=badge or 'Disponible Hoy',
                    activo=activo
                )
                messages.success(request, f"Nuevo servicio '{s.nombre}' creado con éxito.")

            return redirect('admin_servicios')

        elif action == 'toggle':
            if servicio_id:
                s = get_object_or_404(Servicio, id=servicio_id)
                s.activo = not s.activo
                s.save()
                estado = "activado" if s.activo else "pausado"
                messages.success(request, f"Servicio '{s.nombre}' {estado} correctamente.")
                return redirect('admin_servicios')

    servicios = Servicio.objects.select_related('categoria').order_by('categoria__orden', 'orden')
    categorias = Categoria.objects.all().order_by('orden')
    return render(request, 'admin/servicios.html', {
        'servicios': servicios,
        'categorias': categorias,
    })


@login_required(login_url='/admin/login/')
def admin_horarios_view(request):
    """Gestión de horarios (/admin/horarios/)"""
    if not request.user.is_staff:
        return redirect('admin_login')

    fecha_seleccionada = request.GET.get('fecha')
    if fecha_seleccionada:
        try:
            fecha_obj = datetime.strptime(fecha_seleccionada, '%Y-%m-%d').date()
        except ValueError:
            fecha_obj = date.today()
    else:
        fecha_obj = date.today()

    reservas_dia = Reserva.objects.filter(fecha=fecha_obj).select_related('servicio')
    return render(request, 'admin/horarios.html', {
        'fecha_obj': fecha_obj,
        'reservas_dia': reservas_dia,
        'horarios_estandar': HORARIOS_ESTANDAR,
    })
