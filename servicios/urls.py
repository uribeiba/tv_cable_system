from django.urls import path
from .import views
from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
   
    path('', views.dashboard, name='dashboard'),
    path('planes/', views.listar_planes, name='listar_planes'),

    # Rutas para planes
    path('planes/', views.listar_planes, name='listar_planes'),  # Lista de planes
    path('planes/admin/', views.listar_planes_admin, name='listar_planes_admin'),
    path('planes/crear/', views.crear_plan, name='crear_plan'),
    path('planes/editar/<int:plan_id>/', views.editar_plan, name='editar_plan'),
    path('planes/eliminar/<int:plan_id>/', views.eliminar_plan, name='eliminar_plan'),

    # Rutas para clientes
    path('clientes/', views.listar_clientes, name='listar_clientes'),
    path('clientes/registrar/', views.registrar_cliente, name='registrar_cliente'),
    path('clientes/<str:rut>/', views.detalle_cliente, name='detalle_cliente'),
    path('clientes/<str:rut>/agregar_plan/', views.agregar_plan, name='agregar_plan'),
    path('clientes/<int:cliente_id>/registrar_pago/', views.registrar_pago, name='registrar_pago'),
    path('editar_cliente/<int:id>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/detalle/<str:rut>/', views.detalle_cliente, name='detalle_cliente'),
    

    # Rutas para contratos
    path('contratar/', views.contratar_servicio, name='contratar_servicio'),
    path('contratos/', views.listar_contratos, name='listar_contratos'),
    path('contratos/eliminar/<int:contrato_id>/', views.eliminar_contrato, name='eliminar_contrato'),
    path('direcciones/editar/<int:direccion_id>/', views.editar_direccion, name='editar_direccion'),
    
    # cargar excel
    path('cargar-datos/', views.cargar_datos, name='cargar_datos'),
    
     # Registrar Pagos
    path('pagos/registrar/', views.registrar_pago, name='registrar_pago'),
    path('pagos/registrar/<int:contrato_id>/', views.registrar_pago, name='registrar_pago_contrato'),
    path('pagos/', views.listar_pagos, name='listar_pagos'),
    path('pagos/detalle/<int:pago_id>/', views.detalle_pago, name='detalle_pago'),
    path('ajax/cargar-direcciones/', views.cargar_direcciones, name='cargar_direcciones'),
    path('direcciones/crear/<int:cliente_id>/', views.crear_direccion, name='crear_direccion'),
    path('direcciones/eliminar/<int:direccion_id>/', views.eliminar_direccion, name='eliminar_direccion'),
    path('direcciones/nueva/<str:rut>/', views.nueva_direccion, name='nueva_direccion'),
    path('contratos/editar/<int:contrato_id>/', views.editar_contrato, name='editar_contrato'),
    path('clientes/editar/<rut>/', views.editar_cliente, name='editar_cliente'),
    
    
    
    # Reportes
    path('reportes/pagos/', views.reporte_pagos, name='reporte_pagos'),
    path('reportes/pagos_pendientes/', views.reporte_pagos_pendientes, name='reporte_pagos_pendientes'),
    path('reportes/clientes_sin_pagos/', views.reporte_clientes_sin_pagos, name='reporte_clientes_sin_pagos'),
    path('reportes/resumen_mensual/', views.reporte_resumen_mensual, name='reporte_resumen_mensual'),
    path( "reportes/pagos/exportar_excel/",views.exportar_reporte_pagos_excel,name="exportar_reporte_pagos_excel"),
    path('reportes/pagos/pdf/', views.exportar_reporte_pagos_pdf, name='exportar_reporte_pagos_pdf'),
    

]
