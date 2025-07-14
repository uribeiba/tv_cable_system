from servicios.utils import validar_rut

# Ejemplos de RUT válidos
ruts_validos = [
    "12774004-6",  # Ejemplo proporcionado
    "5.497.643-7",
    "22222222-2",
]

# Ejemplos de RUT inválidos
ruts_invalidos = [
    "12774004-5",  # Dígito verificador incorrecto
    "12.774.004-K",  # Dígito verificador incorrecto
    "12345678-9",  # Dígito verificador incorrecto
]

print("### RUTs válidos ###")
for rut in ruts_validos:
    print(f"{rut}: {validar_rut(rut)}")

print("\n### RUTs inválidos ###")
for rut in ruts_invalidos:
    print(f"{rut}: {validar_rut(rut)}")
