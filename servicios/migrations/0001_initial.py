# Generated by Django 5.1.5 on 2025-07-09 20:20

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rut', models.CharField(max_length=12, unique=True)),
                ('nombre', models.CharField(max_length=100)),
                ('apellido', models.CharField(max_length=100)),
                ('correo', models.EmailField(max_length=254)),
                ('telefono', models.CharField(blank=True, max_length=15, null=True)),
                ('sexo', models.CharField(blank=True, choices=[('M', 'Masculino'), ('F', 'Femenino')], max_length=1)),
                ('observaciones', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, verbose_name='Nombre del Plan')),
                ('categoria', models.CharField(choices=[('BASICO', 'Básico'), ('PREMIUM', 'Premium'), ('TERCERA_EDAD', 'Tercera Edad')], max_length=20, verbose_name='Categoría')),
                ('tipo_suscripcion', models.CharField(choices=[('MENSUAL', 'Mensual'), ('ANUAL', 'Anual')], max_length=20, verbose_name='Tipo de Suscripción')),
                ('precio_base', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio Base')),
                ('descuento', models.DecimalField(decimal_places=2, default=0.0, max_digits=5, verbose_name='Descuento para Pago Anual (%)')),
                ('descripcion', models.TextField(blank=True, verbose_name='Descripción')),
            ],
        ),
        migrations.CreateModel(
            name='TipoPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, unique=True, verbose_name='Nombre del Tipo de Plan')),
                ('descripcion', models.TextField(blank=True, null=True, verbose_name='Descripción')),
            ],
        ),
        migrations.CreateModel(
            name='Direccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direccion_instalacion', models.CharField(max_length=255)),
                ('numero_cliente', models.CharField(blank=True, max_length=20, null=True)),
                ('latitud', models.FloatField(blank=True, null=True)),
                ('longitud', models.FloatField(blank=True, null=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='servicios.cliente')),
            ],
        ),
        migrations.CreateModel(
            name='Contrato',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateField(default=django.utils.timezone.now, verbose_name='Fecha de Inicio')),
                ('gracia_dias', models.IntegerField(default=5, verbose_name='Días de Gracia')),
                ('total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Total a Pagar')),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='servicios.cliente', verbose_name='Cliente')),
                ('direccion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='servicios.direccion', verbose_name='Dirección de Instalación')),
                ('planes', models.ManyToManyField(to='servicios.plan', verbose_name='Planes Contratados')),
            ],
        ),
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_pago', models.DateField(default=django.utils.timezone.now, verbose_name='Fecha de Pago')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Monto Pagado')),
                ('metodo_pago', models.CharField(choices=[('EFECTIVO', 'Efectivo'), ('CREDITO', 'Tarjeta de Crédito'), ('DEBITO', 'Tarjeta de Débito'), ('TRANSFERENCIA', 'Transferencia')], max_length=20, verbose_name='Método de Pago')),
                ('periodo_inicio', models.DateField(default=django.utils.timezone.now, verbose_name='Periodo Inicio')),
                ('periodo_fin', models.DateField(default=django.utils.timezone.now, verbose_name='Periodo Fin')),
                ('estado', models.CharField(choices=[('CONFIRMADO', 'Confirmado'), ('PENDIENTE', 'Pendiente')], default='CONFIRMADO', max_length=20, verbose_name='Estado')),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='servicios.cliente', verbose_name='Cliente')),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='servicios.contrato', verbose_name='Contrato')),
            ],
        ),
        migrations.AddField(
            model_name='plan',
            name='tipo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='servicios.tipoplan', verbose_name='Tipo de Plan'),
        ),
    ]
