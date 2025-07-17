from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from .models import Cliente, Plan, Pago, Contrato, Direccion
from .forms import ClienteForm, DireccionForm, ContratoForm, PlanForm, PagoForm, PlanEditForm
from django.contrib.messages import get_messages
import pandas as pd
from django.db import IntegrityError
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db.models import F
from datetime import timedelta
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.db.models import Prefetch
from django.http import JsonResponse
from .forms import ClienteEditForm
from django.db.models import Sum
import openpyxl
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.db.models.functions import TruncMonth
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


# ------------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------------
@login_required
def dashboard(request):
    """
    Vista para el Dashboard principal con estadísticas.
    """

    # Ejemplo de estadísticas:
    pagos_pendientes = Pago.objects.filter(estado='PENDIENTE').count()
    total_pagos = Pago.objects.count()
    total_monto_pagado = Pago.objects.filter(estado='CONFIRMADO').aggregate(total=Sum('monto'))['total'] or 0
    contratos_vencidos = Contrato.objects.filter(activo=False).count()
    ultimos_pagos = Pago.objects.select_related('contrato', 'contrato__cliente').order_by('-fecha_pago')[:5]

    context = {
        'pagos_pendientes': pagos_pendientes,
        'total_pagos': total_pagos,
        'total_monto_pagado': total_monto_pagado,
        'contratos_vencidos': contratos_vencidos,
        'ultimos_pagos': ultimos_pagos,
    }
    return render(request, 'servicios/dashboard.html', context)







# Vista para listar los planes
def listar_planes(request):
    planes = Plan.objects.all()
    return render(request, 'servicios/listar_planes.html', {'planes': planes})


# ------------------------------------------------------------
# Contratar Servicio
# ------------------------------------------------------------
@login_required
def contratar_servicio(request):
    storage = messages.get_messages(request)
    storage.used = True

    if request.method == 'POST':
        form = ContratoForm(request.POST)
        if form.is_valid():
            contrato = form.save(commit=False)

            # Si el usuario no envía fecha, usamos la fecha actual
            if not contrato.fecha_inicio:
                contrato.fecha_inicio = timezone.now()

            # Calcular el total automáticamente
            planes_seleccionados = form.cleaned_data['planes']
            total = sum(plan.obtener_precio() for plan in planes_seleccionados)
            contrato.total = total

            contrato.save()
            form.save_m2m()

            # Calcular el periodo del contrato
            fecha_inicio = contrato.fecha_inicio

            if planes_seleccionados.filter(tipo_suscripcion='ANUAL').exists():
                try:
                    periodo_fin = fecha_inicio.replace(year=fecha_inicio.year + 1)
                except ValueError:
                    # Caso 29 febrero → 28 febrero siguiente
                    periodo_fin = fecha_inicio + timedelta(days=365)
            else:
                periodo_fin = fecha_inicio + timedelta(days=30)

            # Crear pago pendiente
            Pago.objects.create(
                contrato=contrato,
                fecha_pago=fecha_inicio,
                monto=contrato.total,
                metodo_pago='EFECTIVO',
                estado='PENDIENTE',
                periodo_inicio=fecha_inicio,
                periodo_fin=periodo_fin
            )

            messages.success(request, 'El contrato se ha creado correctamente y el pago quedó pendiente.')
            return redirect('listar_contratos')
        else:
            messages.error(request, 'Hubo un error al crear el contrato.')
    else:
        form = ContratoForm()

    # Precios para el cálculo dinámico en JS
    planes = Plan.objects.all()
    precios = {
        plan.id: float(plan.obtener_precio())
        for plan in planes
    }
    precios_json = json.dumps(precios, cls=DjangoJSONEncoder)

    return render(
        request,
        'servicios/contratar_servicio.html',
        {
            'form': form,
            'precios_planes': precios_json
        }
    )

# Vista para registrar clientes
@login_required
def registrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, 'Cliente registrado correctamente.')
            return redirect('listar_clientes')  # ✅ Aquí el nombre correcto
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = ClienteForm()
    
    return render(request, 'servicios/registrar_cliente.html', {'form': form})


# Vista para listar clientes con paginación y búsqueda
@login_required
def listar_clientes(request):
    query = request.GET.get('q', '')
    page_number = request.GET.get('page', 1)

    if query:
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(rut__icontains=query)
        )
    else:
        clientes = Cliente.objects.all()

    paginator = Paginator(clientes, 10)

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        page_obj = paginator.page(1)

    context = {
        'page_obj': page_obj,
        'query': query,
    }

    return render(request, 'servicios/listar_clientes.html', context)


# edita cliente
@login_required
def editar_cliente(request, cliente_id):
    if request.method == 'POST':
        cliente = Cliente.objects.get(id=cliente_id)
        nombre = request.POST.get('nombre_completo')
        rut = request.POST.get('rut')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono', '')
        direccion = request.POST.get('direccion', '')

        # Validaciones
        if not nombre or not rut or not correo:
            messages.error(request, "Los campos Nombre, RUT y Correo Electrónico son obligatorios.")
            return redirect('detalle_cliente', cliente_id=cliente.id)

        if '@' not in correo:
            messages.error(request, "El correo electrónico no es válido.")
            return redirect('detalle_cliente', cliente_id=cliente.id)

        # Actualización de datos
        cliente.nombre_completo = nombre
        cliente.rut = rut
        cliente.correo = correo
        cliente.telefono = telefono
        cliente.direccion = direccion
        cliente.save()

        messages.success(request, "Cliente actualizado correctamente.")
        return redirect('detalle_cliente', cliente_id=cliente.id)


# Vista para mostrar el detalle de un clientede
@login_required
def detalle_cliente(request, rut):
    cliente = get_object_or_404(Cliente, rut=rut)

    # Obtener direcciones del cliente
    direcciones = Direccion.objects.filter(cliente=cliente)

    # Obtener contratos del cliente
    contratos = Contrato.objects.filter(cliente=cliente)

    # Si estás usando formulario para agregar direcciones desde esta vista:
    if request.method == 'POST':
        form = DireccionForm(request.POST)
        if form.is_valid():
            nueva_direccion = form.save(commit=False)
            nueva_direccion.cliente = cliente
            nueva_direccion.save()
            return redirect('detalle_cliente', rut=rut)
    else:
        form = DireccionForm()

    return render(request, 'servicios/detalle_cliente_simple.html', {
        'cliente': cliente,
        'direcciones': direcciones,
        'contratos': contratos,
        'form': form
    })



@login_required
def detalle_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)
    return render(request, 'servicios/detalle_pago.html', {
        'pago': pago,
    })

@login_required
def cargar_direcciones(request):
    cliente_id = request.GET.get('cliente_id')
    direcciones = Direccion.objects.filter(cliente_id=cliente_id)
    
    data = []
    for d in direcciones:
        data.append({
            'id': d.id,
            'text': str(d),  # Esto muestra el __str__ de la dirección
        })

    return JsonResponse(data, safe=False)


# Vista para crear un plan
@login_required
def crear_plan(request):
    if request.method == 'POST':
        form = PlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'El plan se ha creado exitosamente.')
            return redirect('listar_planes_admin')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = PlanForm()

    return render(request, 'servicios/crear_plan.html', {'form': form})


# Vista para listar contratos
@login_required
def listar_contratos(request):
    query = request.GET.get('q')  # Capturar el término de búsqueda
    if query:
        contratos = Contrato.objects.filter(
            cliente__rut__icontains=query
        ) | Contrato.objects.filter(
            cliente__nombre__icontains=query
        ) | Contrato.objects.filter(
            cliente__apellido__icontains=query
        )
    else:
        # Usar nombres únicos para evitar conflictos
        contratos = Contrato.objects.values(
            rut=F('cliente__rut'),
            nombre_cliente=F('cliente__nombre'),
            apellido_cliente=F('cliente__apellido')
        ).distinct()

    # Paginación con 10 contratos por página
    paginator = Paginator(contratos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'servicios/listar_contratos.html', {
        'contratos': page_obj,
        'query': query,
    })

# Vista para editar plan
@login_required
def editar_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)  # Obtener el plan por su ID
    if request.method == 'POST':
        form = PlanEditForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()  # Guardar cambios en el plan
            messages.success(request, 'El plan ha sido actualizado correctamente.')
            return redirect('listar_planes')  # Redirigir a la lista de planes
    else:
        form = PlanEditForm(instance=plan)  # Precargar datos del plan

    return render(request, 'servicios/editar_plan.html', {'form': form, 'plan': plan})



@login_required
def listar_planes_admin(request):
    planes = Plan.objects.all()
    return render(request, 'servicios/listar_planes_admin.html', {'planes': planes})



@login_required
def eliminar_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    if request.method == 'POST':
        plan.delete()
        messages.success(request, 'El plan ha sido eliminado correctamente.')
        return redirect('listar_planes_admin')
    return render(request, 'servicios/eliminar_plan.html', {'plan': plan})


@login_required
def eliminar_contrato(request, contrato_id):
    contrato = get_object_or_404(Contrato, id=contrato_id)
    contrato.delete()
    messages.success(request, 'El contrato ha sido eliminado correctamente.')
    return redirect('listar_contratos')



@login_required
def agregar_plan(request, rut):
    cliente = get_object_or_404(Cliente, rut=rut)
    if request.method == 'POST':
        planes_ids = request.POST.getlist('planes')
        planes = Plan.objects.filter(id__in=planes_ids)
        contrato = Contrato.objects.create(cliente=cliente)
        contrato.planes.set(planes)
        contrato.calcular_total()
        contrato.save()
        messages.success(request, 'El contrato ha sido agregado correctamente.')
        return redirect('detalle_cliente', rut=cliente.rut)

@login_required
def registrar_pago(request, contrato_id=None):
    contrato = None
    total_referencia = None

    contratos_totales = {}
    for c in Contrato.objects.all():
        contratos_totales[c.id] = float(c.total)

    contratos_totales_json = json.dumps(contratos_totales, cls=DjangoJSONEncoder)

    if contrato_id:
        contrato = get_object_or_404(Contrato, id=contrato_id)
        total_referencia = contrato.total

    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.cliente = pago.contrato.cliente
            pago.save()
            messages.success(request, "El pago se ha registrado correctamente.")
            return redirect('listar_pagos')
        else:
            messages.error(request, "Hubo un error al registrar el pago.")
    else:
        initial_data = {}
        if contrato:
            initial_data['contrato'] = contrato
            initial_data['cliente'] = contrato.cliente
        form = PagoForm(initial=initial_data)

    return render(request, 'servicios/registrar_pago.html', {
        'form': form,
        'total_referencia': total_referencia,
        'contrato': contrato,
        'contratos_totales_json': contratos_totales_json,
    })



@login_required
def listar_pagos(request):
    query = request.GET.get('q', '')

    pagos = Pago.objects.select_related('contrato', 'contrato__cliente')

    if query:
        pagos = pagos.filter(
            Q(contrato__cliente__nombre__icontains=query) |
            Q(contrato__cliente__apellido__icontains=query) |
            Q(contrato__id__icontains=query) |
            Q(metodo_pago__icontains=query) |
            Q(estado__icontains=query)
        )

    paginator = Paginator(pagos, 10)  # 10 pagos por página
    page = request.GET.get('page')

    try:
        pagos_page = paginator.page(page)
    except PageNotAnInteger:
        pagos_page = paginator.page(1)
    except EmptyPage:
        pagos_page = paginator.page(paginator.num_pages)

    return render(request, 'servicios/listar_pagos.html', {
        'pagos': pagos_page,
        'query': query
    })

@login_required
def cargar_clientes(request):
    if request.method == 'POST' and 'archivo' in request.FILES:
        archivo = request.FILES['archivo']
        try:
            # Leer el archivo Excel
            df = pd.read_excel(archivo)

            # Normalizar nombres de columnas
            df.columns = df.columns.str.strip().str.upper()

            # Columnas requeridas en mayúsculas
            columnas_requeridas = ['RUT', 'NOMBRE', 'APELLIDOS']
            for col in columnas_requeridas:
                if col not in df.columns:
                    raise ValueError(f"La columna '{col}' no se encuentra en el archivo.")

            # Cargar los datos
            errores = []
            nuevos = []
            actualizados = []

            for index, row in df.iterrows():
                try:
                    cliente, creado = Cliente.objects.update_or_create(
                        rut=row['RUT'],
                        defaults={
                            'nombre': row['NOMBRE'],
                            'apellido': row['APELLIDOS'],  # Cambiar a 'apellido' si es singular
                            'correo': row.get('CORREO', None),
                            'telefono': row.get('TELEFONO', None),
                            'direccion': row.get('DIRECCION', None),
                            'sexo': row.get('SEXO', None),
                        }
                    )
                    if creado:
                        nuevos.append({'fila': index + 1, 'detalle': f"Cliente '{cliente.nombre_completo()}' creado correctamente."})
                    else:
                        actualizados.append({'fila': index + 1, 'detalle': f"Cliente '{cliente.nombre_completo()}' actualizado correctamente."})

                except IntegrityError as e:
                    errores.append({'fila': index + 1, 'columna': 'RUT', 'detalle': f"El RUT {row['RUT']} ya existe en la base de datos."})
                except Exception as e:
                    errores.append({'fila': index + 1, 'columna': '-', 'detalle': f"Error inesperado: {str(e)}"})

            return render(request, 'servicios/cargar_clientes.html', {
                'errores': errores,
                'nuevos': nuevos,
                'actualizados': actualizados,
            })

        except Exception as e:
            return render(request, 'servicios/cargar_clientes.html', {'error': str(e)})

    return render(request, 'servicios/cargar_clientes.html')


@login_required
def cargar_datos(request):
    errores = []
    nuevos = []
    actualizados = []

    if request.method == 'POST' and 'archivo_excel' in request.FILES:
        archivo_excel = request.FILES['archivo_excel']
        try:
            # Leer el archivo Excel
            df = pd.read_excel(archivo_excel)
            df.columns = df.columns.str.strip().str.upper()

            # Verificar que las columnas requeridas existan
            columnas_requeridas = ['RUT', 'NOMBRE', 'APELLIDOS']
            for col in columnas_requeridas:
                if col not in df.columns:
                    raise ValueError(f"La columna '{col}' no se encuentra en el archivo.")

            # Iterar sobre las filas del archivo Excel
            for index, row in df.iterrows():
                try:
                    cliente, creado = Cliente.objects.update_or_create(
                        rut=row['RUT'],
                        defaults={
                            'nombre': row['NOMBRE'],
                            'apellido': row['APELLIDOS'],  # Asegúrate que coincida con el modelo
                            'correo': row.get('CORREO', None),
                            'telefono': row.get('TELEFONO', None),
                            'direccion': row.get('DIRECCION', None),
                            'sexo': row.get('SEXO', None),
                        }
                    )
                    if creado:
                        nuevos.append({'fila': index + 1, 'detalle': f"Cliente '{cliente.nombre_completo()}' creado correctamente."})
                    else:
                        actualizados.append({'fila': index + 1, 'detalle': f"Cliente '{cliente.nombre_completo()}' actualizado correctamente."})
                except IntegrityError as e:
                    errores.append({'fila': index + 1, 'columna': 'RUT', 'detalle': f"Error de integridad: {str(e)}"})
                except Exception as e:
                    errores.append({'fila': index + 1, 'columna': '-', 'detalle': f"Error inesperado: {str(e)}"})

        except Exception as e:
            errores.append({'fila': '-', 'columna': '-', 'detalle': f'Error al leer el archivo: {str(e)}'})

    return render(request, 'servicios/cargar_clientes.html', {
        'errores': errores,
        'nuevos': nuevos,
        'actualizados': actualizados,
    })


# views pata editar direccion
@login_required
def editar_direccion(request, direccion_id):
    direccion = get_object_or_404(Direccion, pk=direccion_id)

    if request.method == 'POST':
        form = DireccionForm(request.POST, instance=direccion)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Dirección actualizada correctamente!")
            return redirect('detalle_cliente', rut=direccion.cliente.rut)
        else:
            messages.error(request, "Hubo un error al actualizar la dirección.")
    else:
        form = DireccionForm(instance=direccion)

    return render(request, 'servicios/editar_direccion.html', {'form': form, 'direccion': direccion})

@login_required
def crear_direccion(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)

    if request.method == 'POST':
        form = DireccionForm(request.POST)
        if form.is_valid():
            nueva_direccion = form.save(commit=False)
            nueva_direccion.cliente = cliente
            nueva_direccion.save()
            messages.success(request, "¡Dirección creada exitosamente!")
            return redirect('detalle_cliente', rut=cliente.rut)
        else:
            messages.error(request, "Hubo un error al crear la dirección.")
    else:
        form = DireccionForm()

    return render(request, 'servicios/crear_direccion.html', {
        'form': form,
        'cliente': cliente,
    })


@login_required
def eliminar_direccion(request, direccion_id):
    direccion = get_object_or_404(Direccion, pk=direccion_id)

    if request.method == 'POST':
        cliente_rut = direccion.cliente.rut
        direccion.delete()
        messages.success(request, "¡Dirección eliminada correctamente!")
        return redirect('detalle_cliente', rut=cliente_rut)

    return render(request, 'servicios/eliminar_direccion.html', {
        'direccion': direccion
    })
    
    
@login_required
def nueva_direccion(request, rut):
    cliente = get_object_or_404(Cliente, rut=rut)

    if request.method == 'POST':
        form = DireccionForm(request.POST)
        if form.is_valid():
            nueva = form.save(commit=False)
            nueva.cliente = cliente
            nueva.save()
            return redirect('detalle_cliente', rut=rut)
    else:
        form = DireccionForm()

    return render(request, 'servicios/nueva_direccion.html', {
        'form': form,
        'cliente': cliente,
    })
    
@login_required
def editar_contrato(request, contrato_id):
    contrato = get_object_or_404(Contrato, id=contrato_id)

    if request.method == 'POST':
        form = ContratoForm(request.POST, instance=contrato)
        if form.is_valid():
            form.save()
            return redirect('detalle_cliente', rut=contrato.cliente.rut)
    else:
        form = ContratoForm(instance=contrato)

    return render(request, 'servicios/editar_contrato.html', {
        'form': form,
        'contrato': contrato,
    })
    
@login_required
def editar_cliente(request, rut):
    cliente = get_object_or_404(Cliente, rut=rut)

    if request.method == 'POST':
        form = ClienteEditForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Los datos del cliente se actualizaron correctamente.')
            return redirect('detalle_cliente', rut=cliente.rut)
        else:
            messages.error(request, 'Hubo un error al actualizar los datos del cliente.')
    else:
        form = ClienteEditForm(instance=cliente)

    return render(request, 'servicios/editar_cliente.html', {'form': form, 'cliente': cliente})




# ------------------------------------------------------------
# Reporte de Pagos
# ------------------------------------------------------------
@login_required
def reporte_pagos(request):
    pagos = Pago.objects.select_related('contrato__cliente').order_by('-fecha_pago')

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if fecha_inicio:
        pagos = pagos.filter(fecha_pago__gte=fecha_inicio)
    if fecha_fin:
        pagos = pagos.filter(fecha_pago__lte=fecha_fin)

    # Total pagado filtrado
    total_pagado = pagos.aggregate(total=Sum('monto'))['total'] or 0

    # Paginación
    paginator = Paginator(pagos, 10)  # 10 pagos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'pagos': page_obj,  # esto se itera en la tabla
        'page_obj': page_obj,  # esto se usa en el paginador
        'total_pagado': total_pagado,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }

    return render(request, 'servicios/reportes/reporte_pagos.html', context)


# ------------------------------------------------------------
# Reporte de Pagos Pendientes
# ------------------------------------------------------------
@login_required
def reporte_pagos_pendientes(request):
    pagos = Pago.objects.select_related('contrato', 'contrato__cliente').filter(estado='PENDIENTE')
    return render(request, 'servicios/reportes/reporte_pagos_pendientes.html', {
        'pagos': pagos
    })

# ------------------------------------------------------------
# Reporte de Clientes sin Pagos
# ------------------------------------------------------------
@login_required
def reporte_clientes_sin_pagos(request):
    # Filtramos los clientes sin pagos
    clientes_sin_pagos = Cliente.objects.filter(contrato__isnull=True)

    # Paginador
    paginator = Paginator(clientes_sin_pagos, 10)  # Muestra 10 clientes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'clientes': page_obj,    # se itera en la tabla
        'page_obj': page_obj,    # se usa en el paginador
    }

    return render(request, 'servicios/reportes/reporte_clientes_sin_pagos.html', context)


# ------------------------------------------------------------
# Reporte Resumen Mensual de Pagos
# ------------------------------------------------------------
@login_required
def reporte_resumen_mensual(request):
    resumen = (
        Pago.objects
        .values(mes=TruncMonth('fecha_pago'))
        .annotate(total=Sum('monto'))
        .order_by('mes')
    )
    return render(request, 'servicios/reportes/reporte_resumen_mensual.html', {
        'resumen': resumen
    })
    
    


def exportar_reporte_pagos_excel(request):
    # Trae todos los pagos (puedes filtrar si quieres)
    pagos = Pago.objects.select_related("contrato").all()

    data = []
    for pago in pagos:
        data.append({
            "Contrato ID": pago.contrato.id,
            "Cliente": pago.contrato.cliente.nombre_completo(),
            "Monto Pagado": float(pago.monto),
            "Fecha Pago": pago.fecha_pago.strftime("%d/%m/%Y"),
            "Método": pago.metodo_pago,
            "Estado": pago.estado,
        })

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"reporte_pagos_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'

    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Pagos")

    return response


def exportar_reporte_pagos_pdf(request):
    """
    Exporta el reporte de pagos en PDF.
    """

    pagos = Pago.objects.select_related('contrato__cliente').order_by('-fecha_pago')

    template_path = 'servicios/reportes/reporte_pagos_pdf.html'
    context = {'pagos': pagos}
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_pagos.pdf"'

    pisa_status = pisa.CreatePDF(
        src=html,
        dest=response,
        encoding='utf-8'
    )

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)

    return response


@require_POST
def eliminar_cliente(request, rut):
    cliente = get_object_or_404(Cliente, rut=rut)
    if request.method == "POST":
        cliente.delete()
        return redirect('listar_clientes')
    return render(request, 'confirmar_eliminacion.html', {'cliente': cliente})
