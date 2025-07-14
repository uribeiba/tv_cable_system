from django.contrib import admin
from .models import Cliente, Direccion, Contrato, Plan, Pago, TipoPlan

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['rut', 'nombre', 'apellido', 'correo', 'telefono']

@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ['direccion_instalacion', 'numero_cliente', 'latitud', 'longitud', 'cliente']

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'fecha_inicio', 'total']


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'mostrar_precio', 'tipo_suscripcion', 'categoria']

    def mostrar_precio(self, obj):
        return "${:,.0f}".format(obj.obtener_precio())

    mostrar_precio.short_description = 'Precio'


@admin.register(TipoPlan)
class TipoPlanAdmin(admin.ModelAdmin):
    list_display = ['nombre']

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['id', 'contrato', 'fecha_pago', 'monto', 'metodo_pago', 'estado']
