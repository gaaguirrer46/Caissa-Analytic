"""Adaptador secundario de hash de contraseñas usando PBKDF2-HMAC-SHA256.

Formato vigente (compacto, <= 100 caracteres para respetar ``usuarios.hash_contrasena``):

 pbkdf2_sha256$<iteraciones>$<sal_b64>$<digest_b64>

Se mantiene compatibilidad de *verificación* con dos formatos históricos:

1. ``pbkdf2:sha256:<iteraciones>$<sal>$<digest>`` (118 caracteres, excedía el
 ``VARCHAR(100)`` del modelo oficial).
2. ``pbkdf2:sha256:hash_<sufijo>``: marcador de demostración usado por los datos
 de prueba de ``BD profesor.txt``. Sólo se acepta si la contraseña coincide
 **exactamente** con el sufijo; nunca por coincidencia parcial."""
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

from dominio.comun.errores import ErrorValidacion
from dominio.usuarios.puertos import ServicioHashContrasenas

_ITERACIONES_POR_DEFECTO = 100_000
_PREFIJO_ACTUAL = "pbkdf2_sha256"
_PREFIJO_LEGADO = "pbkdf2:sha256:"
_PREFIJO_DEMO = "pbkdf2:sha256:hash_"

def _b64crudo(datos: bytes) -> str:
    """Codifica en Base64 sin relleno (compacto y seguro para VARCHAR)."""
    return base64.b64encode(datos).decode("ascii").rstrip("=")

def _b64decodificar(texto: str) -> bytes:
    relleno = "=" * (-len(texto) % 4)
    return base64.b64decode(texto + relleno, validate=True)

class ServicioHashPbkdf2(ServicioHashContrasenas):
    """Implementación de hash seguro con PBKDF2-HMAC-SHA256 sin librerías externas."""

    ITERACIONES = _ITERACIONES_POR_DEFECTO
    HASH_DUMMY = (
        f"{_PREFIJO_ACTUAL}${_ITERACIONES_POR_DEFECTO}$"
        f"{_b64crudo(bytes(16))}${_b64crudo(bytes(32))}"
    )

    ADVERTENCIA_HASH_DEMO = (
        "Los hashes 'pbkdf2:sha256:hash_*' son marcadores de demostración de "
        "BD profesor.txt y no deben usarse en producción."
    )

    def hash_dummy(self) -> str:
        """Hash sintético con el mismo costo de cómputo que un hash real."""
        return self.HASH_DUMMY

    def hashear(self, contrasena_plana: str) -> str:
        if not isinstance(contrasena_plana, str) or not contrasena_plana:
            raise ErrorValidacion(
                "La contraseña a hashear debe ser una cadena no vacía."
            )
        sal = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            contrasena_plana.encode("utf-8"),
            sal,
            self.ITERACIONES,
        )
        return f"{_PREFIJO_ACTUAL}${self.ITERACIONES}${_b64crudo(sal)}${_b64crudo(digest)}"

    def _consumir_tiempo_constante(self) -> None:
        """Ejecuta un PBKDF2 sintético para igualar el costo de todas las ramas.

 Sin esto, un hash de demostración o un formato corrupto se rechazan con
 una comparación de cadenas (microsegundos), mientras que un hash real
 tarda ~100 ms: la diferencia permite enumerar cuentas por temporización.
 """
        hashlib.pbkdf2_hmac(
            "sha256", b"dummy", bytes(16), self.ITERACIONES
        )

    def verificar(self, contrasena_plana: str, hash_almacenado: str) -> bool:
        if (
            not isinstance(contrasena_plana, str)
            or not contrasena_plana
            or not isinstance(hash_almacenado, str)
            or not hash_almacenado
        ):
            self._consumir_tiempo_constante()
            return False

        if hash_almacenado.startswith(_PREFIJO_DEMO):

            self._consumir_tiempo_constante()
            sufijo = hash_almacenado[len(_PREFIJO_DEMO) :]
            return bool(sufijo) and hmac.compare_digest(contrasena_plana, sufijo)

        if hash_almacenado.startswith(_PREFIJO_ACTUAL + "$"):
            return self._verificar_compacto(contrasena_plana, hash_almacenado)

        if hash_almacenado.startswith(_PREFIJO_LEGADO):
            return self._verificar_legado(contrasena_plana, hash_almacenado)

        self._consumir_tiempo_constante()
        return False

    def _verificar_compacto(self, contrasena_plana: str, hash_almacenado: str) -> bool:
        try:
            _, iteraciones_txt, sal_txt, digest_txt = hash_almacenado.split("$")
            iteraciones = int(iteraciones_txt)
            sal = _b64decodificar(sal_txt)
            digest_esperado = _b64decodificar(digest_txt)
        except (ValueError, TypeError):
            self._consumir_tiempo_constante()
            return False

        calculado = hashlib.pbkdf2_hmac(
            "sha256", contrasena_plana.encode("utf-8"), sal, iteraciones
        )
        return hmac.compare_digest(calculado, digest_esperado)

    def _verificar_legado(self, contrasena_plana: str, hash_almacenado: str) -> bool:
        try:
            datos = hash_almacenado[len(_PREFIJO_LEGADO) :]
            partes = datos.split("$")
            if len(partes) == 3:
                iteraciones_str, sal, digest_esperado = partes
                iteraciones = int(iteraciones_str)
            elif len(partes) == 2:
                sal, digest_esperado = partes
                iteraciones = self.ITERACIONES
            else:
                self._consumir_tiempo_constante()
                return False

            calculado = hashlib.pbkdf2_hmac(
                "sha256",
                contrasena_plana.encode("utf-8"),
                sal.encode("utf-8"),
                iteraciones,
            ).hex()
            return hmac.compare_digest(calculado, digest_esperado)
        except (ValueError, TypeError):
            self._consumir_tiempo_constante()
            return False
