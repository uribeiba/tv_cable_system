import re
from django.core.exceptions import ValidationError

def validar_rut(rut):
    """
    Valida un RUT chileno.
    Formato válido: 12345678-9 o 12.345.678-9
    """
    # Eliminar puntos y guiones, y convertir a mayúsculas
    rut = rut.upper().replace(".", "").replace("-", "")
    print(f"RUT procesado: {rut}")  # Log para depuración

    # Verificar que el RUT tenga al menos 8 dígitos más el dígito verificador
    if not re.match(r'^\d{7,8}[0-9K]$', rut):
        raise ValidationError("El RUT ingresado tiene un formato incorrecto. Ejemplo: 12345678-9")

    # Separar el cuerpo del RUT y el dígito verificador
    cuerpo = rut[:-1]
    dv = rut[-1]
    print(f"Cuerpo: {cuerpo}, DV ingresado: {dv}")  # Log para depuración

    # Calcular el dígito verificador esperado
    suma = 0
    multiplo = 2

    for c in reversed(cuerpo):
        suma += int(c) * multiplo
        multiplo = 2 if multiplo == 7 else multiplo + 1

    resto = suma % 11
    dv_calculado = "K" if resto == 10 else str(11 - resto if resto != 0 else 0)
    print(f"DV calculado: {dv_calculado}")  # Log para depuración

    # Validar el dígito verificador
    if dv != dv_calculado:
        raise ValidationError("El RUT ingresado no es válido.")




def es_rut_valido(rut):
    """
    Valida si el RUT es correcto. Requiere que el formato sea XXXXXXXX-X.
    """
    # Validar formato general
    if not re.match(r"^\d{7,8}-[0-9kK]$", rut):
        return False

    # Separar el número del dígito verificador
    cuerpo, dv = rut.split("-")
    cuerpo = int(cuerpo)
    dv = dv.upper()

    # Calcular dígito verificador
    suma = 0
    multiplicador = 2

    for digito in reversed(str(cuerpo)):
        suma += int(digito) * multiplicador
        multiplicador = 9 if multiplicador == 7 else multiplicador + 1

    mod11 = 11 - (suma % 11)
    dv_calculado = "K" if mod11 == 10 else "0" if mod11 == 11 else str(mod11)

    # Comparar dígito verificador calculado con el ingresado
    return dv == dv_calculado
