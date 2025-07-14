from django import forms
from .models import Cliente, Contrato, Plan, Direccion, Pago
from .utils import validar_rut  # Importación del validador de RUT
from django.core.exceptions import ValidationError
from .models import Direccion


# -----------------------------------------------
# Formulario para el modelo Cliente
# -----------------------------------------------
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'rut',
            'nombre',
            'apellido',
            'correo',
            'telefono',
            'sexo',
            'observaciones'
        ]
        widgets = {
            'correo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo Electrónico (opcional)'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono'
            }),
            'observaciones': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Observaciones'
            }),
        }

    # Validador personalizado para el campo RUT
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        validar_rut(rut)  # Utiliza la función de validación importada
        return rut

    # Validador para limpiar campo correo vacío
    def clean_correo(self):
        data = self.cleaned_data.get('correo')
        if data == "":
            return None
        return data





# -----------------------------------------------
# Formulario para el modelo Contrato
# -----------------------------------------------

class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['direccion_instalacion', 'numero_cliente', 'latitud', 'longitud', 'cliente']


class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ['cliente', 'direccion', 'planes', 'total']
        labels = {
            'cliente': 'Seleccione el Cliente',
            'direccion': 'Dirección de Instalación',
            'planes': 'Planes Contratados',
            'total': 'Total del Contrato (CLP)',
        }
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'direccion': forms.Select(attrs={'class': 'form-select'}),
            'planes': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'total': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el total del contrato'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mostrar clientes ordenados por nombre y apellido
        self.fields['cliente'].queryset = Cliente.objects.order_by('nombre', 'apellido')

        # Ordenar direcciones por dirección_instalacion
        self.fields['direccion'].queryset = Direccion.objects.order_by('direccion_instalacion')

        # Ordenar planes por nombre
        self.fields['planes'].queryset = Plan.objects.order_by('nombre')



# -----------------------------------------------
# Formulario para crear un Plan
# -----------------------------------------------
class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['nombre', 'tipo', 'categoria', 'tipo_suscripcion', 'precio_base', 'descuento', 'descripcion']  # Campos del modelo Plan
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'tipo_suscripcion': forms.Select(attrs={'class': 'form-select'}),
            'precio_base': forms.NumberInput(attrs={'class': 'form-control'}),
            'descuento': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


# -----------------------------------------------
# Formulario para editar un Plan
# -----------------------------------------------
class PlanEditForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['nombre', 'tipo', 'categoria', 'tipo_suscripcion', 'precio_base', 'descuento', 'descripcion']  # Igual que PlanForm, pero más enfocado en edición
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'tipo_suscripcion': forms.Select(attrs={'class': 'form-select'}),
            'precio_base': forms.NumberInput(attrs={'class': 'form-control'}),
            'descuento': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


# -----------------------------------------------
# Formulario para el modelo Pago
# -----------------------------------------------
class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['contrato', 'fecha_pago', 'monto', 'metodo_pago',
                  'periodo_inicio', 'periodo_fin', 'estado']
        widgets = {
            'fecha_pago': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }, format='%Y-%m-%d'),
            'periodo_inicio': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }, format='%Y-%m-%d'),
            'periodo_fin': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['fecha_pago', 'periodo_inicio', 'periodo_fin']:
            self.fields[field].input_formats = ['%Y-%m-%d']


# -----------------------------------------------
# Formulario genérico para cargar archivos
# -----------------------------------------------
class CargarArchivoForm(forms.Form):
    archivo = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label="Seleccione un archivo para cargar"
    )



# -----------------------------------------------
# Formularios para Editar
# -----------------------------------------------
class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['direccion_instalacion', 'numero_cliente', 'latitud', 'longitud']
        widgets = {
            'direccion_instalacion': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_cliente': forms.TextInput(attrs={'class': 'form-control'}),
            'latitud': forms.NumberInput(attrs={'class': 'form-control'}),
            'longitud': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ClienteEditForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['correo', 'telefono']
        labels = {
            'correo': 'Correo Electrónico',
            'telefono': 'Teléfono'
        }
        widgets = {
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
        
def editar_cliente(request, rut):
    cliente = get_object_or_404(Cliente, rut=rut)

    if request.method == 'POST':
        form = ClienteEditForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos del cliente actualizados correctamente.')
            return redirect('detalle_cliente', rut=cliente.rut)
        else:
            messages.error(request, 'Hubo un error al actualizar los datos.')
    else:
        form = ClienteEditForm(instance=cliente)

    return render(request, 'servicios/editar_cliente.html', {'form': form, 'cliente': cliente})