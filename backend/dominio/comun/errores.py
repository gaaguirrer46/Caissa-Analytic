class ErrorDeDominio(Exception):
    """Error base de la capa de dominio."""

class ErrorValidacion(ErrorDeDominio):
    """Error por violación de una regla de negocio o validación."""

class ErrorAutenticacion(ErrorDeDominio):
    """Error de credenciales o autorización."""

class EntidadNoEncontrada(ErrorDeDominio):
    """Error cuando una entidad requerida no existe."""
