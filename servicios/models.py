from django.db import models
from django.utils.translation import gettext_lazy as _
from .utils import es_rut_valido
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# ------------------------------------------------------------
# MODELO TIPO DE PLAN
# ------------------------------------------------------------
class TipoPlan(models.Model):
    nombre = models.CharField(max_length=50, verbose_name=_("Nombre del Tipo de Plan"))

    def __str__(self):
        return self.nombre


# ------------------------------------------------------------
# MODELO PLAN
# ------------------------------------------------------------
class Plan(models.Model):
    CATEGORIAS = [
        ('BASICO', 'Básico'),
        ('PREMIUM', 'Premium'),
        ('TERCERA_EDAD', 'Tercera Edad'),
    ]

    TIPOS_SUSCRIPCION = [
        ('MENSUAL', 'Mensual'),
        ('ANUAL', 'Anual'),
    ]

    nombre = models.CharField(max_length=50, verbose_name=_("Nombre del Plan"))
    tipo = models.ForeignKey(TipoPlan, on_delete=models.CASCADE, verbose_name=_("Tipo de Plan"))
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, verbose_name=_("Categoría"))
    tipo_suscripcion = models.CharField(max_length=20, choices=TIPOS_SUSCRIPCION, verbose_name=_("Tipo de Suscripción"))
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Precio Base"))
    descuento = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_("Descuento para Pago Anual (%)"), default=0.0)
    descripcion = models.TextField(verbose_name=_("Descripción"), blank=True)

    def obtener_precio(self):
        if self.tipo_suscripcion == 'ANUAL':
            return self.precio_base * (1 - self.descuento / 100)
        return self.precio_base

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_suscripcion_display()})"

# ------------------------------------------------------------
# MODELO CLIENTE
# ------------------------------------------------------------
class Cliente(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    rut = models.CharField(max_length=20, unique=True, verbose_name=_("RUT"))
    nombre = models.CharField(max_length=100, verbose_name=_("Nombre"))
    apellido = models.CharField(max_length=100, verbose_name=_("Apellido"))
    correo = models.CharField(
        max_length=254,
        verbose_name=_("Correo Electrónico"),
        blank=True,
        null=True
    )
    telefono = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Teléfono"))
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, verbose_name=_("Sexo"))
    direccion_personal = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Dirección Personal"))
    observaciones = models.TextField(blank=True, null=True, verbose_name=_("Observaciones"))

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def __str__(self):
        return self.nombre_completo()



# ------------------------------------------------------------
# MODELO DIRECCIÓN DE INSTALACIÓN
# ------------------------------------------------------------
class Direccion(models.Model):
   
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name=_("Cliente"))
    direccion_instalacion = models.CharField(max_length=255, verbose_name=_("Dirección de Instalación"))
    numero_cliente = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Número de Cliente"))
    latitud = models.FloatField(blank=True, null=True, verbose_name=_("Latitud"))
    longitud = models.FloatField(blank=True, null=True, verbose_name=_("Longitud"))

    def __str__(self):
        return f"{self.direccion_instalacion} - {self.cliente.nombre_completo()}"


# ------------------------------------------------------------
# MODELO CONTRATO
# ------------------------------------------------------------

class Contrato(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name=_("Cliente"))
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE, verbose_name=_("Dirección de Instalación"))
    planes = models.ManyToManyField(Plan, verbose_name=_("Planes Contratados"))
    fecha_inicio = models.DateField(verbose_name=_("Fecha de Inicio del Contrato"), null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Total"), default=0)
    activo = models.BooleanField(default=True, verbose_name=_("Activo"))

    def calcular_total(self):
        total = sum([p.obtener_precio() for p in self.planes.all()])
        self.total = total
        self.save()

    def __str__(self):
      
        return self.cliente.nombre_completo() if self.cliente else "Cliente desconocido"



# ------------------------------------------------------------
# MODELO PAGO
# ------------------------------------------------------------
class Pago(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADO', 'Confirmado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    METODOS_PAGO = [
        ('EFECTIVO', 'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('TARJETA', 'Tarjeta'),
    ]

    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, verbose_name=_("Contrato"))
    fecha_pago = models.DateField(verbose_name=_("Fecha de Pago"))
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Monto Pagado"))
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, verbose_name=_("Método de Pago"))
    periodo_inicio = models.DateField(verbose_name=_("Periodo Inicio"))
    periodo_fin = models.DateField(verbose_name=_("Periodo Fin"))
    estado = models.CharField(max_length=20, choices=ESTADOS, verbose_name=_("Estado"))

    def __str__(self):
        return f"Pago {self.id} - Contrato {self.contrato.id}"
