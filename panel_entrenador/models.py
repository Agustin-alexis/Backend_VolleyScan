"""Modelos del panel de entrenador sobre las tablas YA EXISTENTES de MySQL.

Todos son `managed = False`: Django solo lee y escribe filas; nunca crea,
altera ni borra tablas. El esquema lo gobierna el script SQL del proyecto
(volleyscan + 002_analisis_remate.sql), así que NO hace falta `makemigrations`.

Notas de diseño:
- Las claves foráneas usan on_delete=DO_NOTHING y db_constraint=False: los
  ON DELETE CASCADE / SET NULL los ejecuta MySQL, no Django.
- Los ENUM de MySQL se declaran con `choices` para que los serializers
  rechacen valores inválidos con un 400 en vez de provocar un error 500.
- Los TINYINT UNSIGNED llevan MaxValueValidator(255) por la misma razón.
"""
from django.core.validators import MaxValueValidator
from django.db import models

TINY = [MaxValueValidator(255)]  # TINYINT UNSIGNED


def _choices(*valores):
    return [(v, v) for v in valores]


NIVELES_USUARIO = _choices("principiante", "intermedio", "avanzado", "profesional")
POSICIONES = _choices("opuesto", "armador", "central", "punta", "libero")
NIVELES_RUTINA = _choices("principiante", "intermedio", "avanzado")
TIPOS_EVENTO = _choices("entrenamiento", "partido", "evaluacion", "reunion", "otro")
ESTADOS_EVENTO = _choices("programado", "en_curso", "completado", "cancelado")
CATEGORIAS_PLANTILLA = _choices(
    "fuerza", "tecnica", "resistencia", "velocidad", "flexibilidad", "tactica"
)


def _fk(modelo, columna, *, related_name="+", null=False):
    return models.ForeignKey(
        modelo,
        db_column=columna,
        on_delete=models.DO_NOTHING,
        db_constraint=False,
        related_name=related_name,
        null=null,
        blank=null,
    )


class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.CharField(max_length=150)
    password_hash = models.CharField(max_length=255)
    rol = models.CharField(max_length=20, null=True)
    nivel = models.CharField(max_length=20, choices=NIVELES_USUARIO, null=True)
    posicion = models.CharField(max_length=20, choices=POSICIONES, null=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    estatura = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    fecha_nac = models.DateField(null=True)
    foto_url = models.CharField(max_length=500, null=True)
    activo = models.BooleanField(null=True)
    creado_en = models.DateTimeField(null=True)
    actualizado_en = models.DateTimeField(null=True)

    # DRF/Django tratan a esta clase como "usuario autenticado" (request.user).
    is_authenticated = True
    is_anonymous = False

    class Meta:
        managed = False
        db_table = "usuarios"


class Configuracion(models.Model):
    id = models.AutoField(primary_key=True)
    usuario_id = models.IntegerField(unique=True)
    unidad_medida = models.CharField(
        max_length=10, default="metric", choices=_choices("metric", "imperial")
    )
    idioma = models.CharField(max_length=2, default="es", choices=_choices("es", "en", "pt"))
    tema = models.CharField(max_length=10, default="dark", choices=_choices("dark", "light", "auto"))
    calidad_video = models.CharField(
        max_length=10, default="alta", choices=_choices("baja", "media", "alta", "auto")
    )
    guardar_videos = models.BooleanField(default=True)
    notif_sesion = models.BooleanField(default=True)
    notif_analisis = models.BooleanField(default=True)
    notif_contenido = models.BooleanField(default=False)
    compartir_progreso = models.BooleanField(default=True)
    permitir_comentarios = models.BooleanField(default=False)
    visibilidad_analisis = models.CharField(
        max_length=12,
        default="solo",
        choices=_choices("solo", "entrenador", "equipo", "todos"),
    )

    class Meta:
        managed = False
        db_table = "configuracion"


class Equipo(models.Model):
    id = models.AutoField(primary_key=True)
    entrenador_id = models.IntegerField()
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50, null=True, blank=True)
    temporada = models.CharField(max_length=20, null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "equipos"


class EquipoDeportista(models.Model):
    id = models.AutoField(primary_key=True)
    equipo = _fk(Equipo, "equipo_id", related_name="integrantes")
    deportista = _fk(Usuario, "deportista_id", related_name="membresias")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    posicion = models.CharField(max_length=50, null=True, blank=True)
    numero_camiseta = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "equipo_deportista"


class Horario(models.Model):
    id = models.BigAutoField(primary_key=True)
    entrenador_id = models.IntegerField()
    equipo = _fk(Equipo, "equipo_id", null=True)
    deportista = _fk(Usuario, "deportista_id", null=True)
    titulo = models.CharField(max_length=150)
    tipo_evento = models.CharField(max_length=20, choices=TIPOS_EVENTO, default="entrenamiento")
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    ubicacion = models.CharField(max_length=150, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_EVENTO, default="programado")
    notas = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "horarios"


class RutinaPlantilla(models.Model):
    id = models.AutoField(primary_key=True)
    entrenador_id = models.IntegerField()
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(null=True, blank=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS_PLANTILLA)
    nivel = models.CharField(max_length=20, choices=NIVELES_RUTINA, default="intermedio")
    duracion_minutos = models.PositiveSmallIntegerField(default=60)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "rutinas_plantillas"


class PlantillaEjercicio(models.Model):
    id = models.AutoField(primary_key=True)
    plantilla = _fk(RutinaPlantilla, "rutina_plantilla_id", related_name="ejercicios")
    nombre_ejercicio = models.CharField(max_length=150)
    series = models.PositiveSmallIntegerField(null=True, blank=True)
    repeticiones = models.CharField(max_length=30, null=True, blank=True)
    descanso_segundos = models.PositiveSmallIntegerField(null=True, blank=True)
    orden = models.PositiveSmallIntegerField(default=1)
    notas = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "plantilla_ejercicios"
        ordering = ["orden", "id"]


class Rutina(models.Model):
    """Rutina personal del atleta (copia asignada por el entrenador)."""

    id = models.AutoField(primary_key=True)
    usuario = _fk(Usuario, "usuario_id")
    entrenador_id = models.IntegerField(null=True)
    plantilla_id = models.IntegerField(null=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(null=True, blank=True)
    nivel = models.CharField(max_length=20, choices=NIVELES_RUTINA, default="intermedio")
    objetivo = models.CharField(max_length=255, null=True, blank=True)
    generada_por_ia = models.BooleanField(default=False)
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "rutinas"


class EjercicioRutina(models.Model):
    id = models.AutoField(primary_key=True)
    rutina = _fk(Rutina, "rutina_id", related_name="ejercicios")
    nombre = models.CharField(max_length=150)
    series = models.PositiveSmallIntegerField(default=3, validators=TINY)
    repeticiones = models.PositiveSmallIntegerField(default=10, validators=TINY)
    orden = models.PositiveSmallIntegerField(default=1, validators=TINY)
    completado = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "ejercicios_rutina"


class Partido(models.Model):
    id = models.AutoField(primary_key=True)
    entrenador_id = models.IntegerField()
    equipo = _fk(Equipo, "equipo_id", related_name="partidos")
    horario = _fk(Horario, "horario_id", null=True)
    rival = models.CharField(max_length=150)
    fecha = models.DateField()
    sets_ganados = models.PositiveSmallIntegerField(default=0, validators=TINY)
    sets_perdidos = models.PositiveSmallIntegerField(default=0, validators=TINY)
    ubicacion = models.CharField(max_length=150, null=True, blank=True)
    notas = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "partidos"


class EstadisticaJugador(models.Model):
    id = models.BigAutoField(primary_key=True)
    partido = _fk(Partido, "partido_id", related_name="estadisticas")
    deportista = _fk(Usuario, "deportista_id")
    saques_exitosos = models.PositiveSmallIntegerField(default=0)
    saques_fallidos = models.PositiveSmallIntegerField(default=0)
    ataques_exitosos = models.PositiveSmallIntegerField(default=0)
    ataques_fallidos = models.PositiveSmallIntegerField(default=0)
    bloqueos = models.PositiveSmallIntegerField(default=0)
    recepciones_exitosas = models.PositiveSmallIntegerField(default=0)
    recepciones_falladas = models.PositiveSmallIntegerField(default=0)
    errores_no_forzados = models.PositiveSmallIntegerField(default=0)
    puntos_totales = models.PositiveSmallIntegerField(default=0)
    minutos_jugados = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "estadisticas_jugador"


class SesionAnalisis(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = _fk(Usuario, "usuario_id")
    entrenador_id = models.IntegerField(null=True)
    cliente_uuid = models.CharField(max_length=36, null=True)
    tecnica = models.CharField(max_length=20)
    puntuacion = models.PositiveSmallIntegerField(null=True)
    total_repeticiones = models.PositiveSmallIntegerField(default=0)
    repeticiones_validas = models.PositiveSmallIntegerField(default=0)
    mejor_puntuacion = models.PositiveSmallIntegerField(null=True)
    duracion_seg = models.PositiveSmallIntegerField(null=True)
    video_url = models.CharField(max_length=500, null=True)
    miniatura_url = models.CharField(max_length=500, null=True)
    modelo_ia = models.CharField(max_length=50, null=True)
    version_estandar = models.CharField(max_length=10, null=True)
    creado_en = models.DateTimeField(null=True)
    revisado_por_entrenador = models.BooleanField(default=False)
    fecha_revision = models.DateTimeField(null=True)

    class Meta:
        managed = False
        db_table = "sesiones_analisis"


class ErrorDetectado(models.Model):
    id = models.AutoField(primary_key=True)
    sesion = _fk(SesionAnalisis, "sesion_id", related_name="errores")
    tipo_error = models.CharField(max_length=100)
    severidad = models.CharField(max_length=10, null=True)
    ocurrencias = models.PositiveSmallIntegerField(null=True)
    descripcion = models.TextField(null=True)

    class Meta:
        managed = False
        db_table = "errores_detectados"


class PuntoClave(models.Model):
    id = models.AutoField(primary_key=True)
    sesion = _fk(SesionAnalisis, "sesion_id", related_name="puntos")
    nombre = models.CharField(max_length=100)
    aprobado = models.BooleanField(null=True)
    angulo_grados = models.DecimalField(max_digits=6, decimal_places=2, null=True)

    class Meta:
        managed = False
        db_table = "puntos_clave"


class RepeticionAnalisis(models.Model):
    id = models.BigAutoField(primary_key=True)
    sesion = _fk(SesionAnalisis, "sesion_id", related_name="repeticiones")
    numero = models.PositiveSmallIntegerField()
    registrada_en = models.DateTimeField()
    valida = models.BooleanField(default=True)
    puntuacion = models.PositiveSmallIntegerField(null=True)
    brazo = models.CharField(max_length=10, null=True)
    motivo_descarte = models.CharField(max_length=255, null=True)
    duracion_vuelo_ms = models.PositiveSmallIntegerField(null=True)
    altura_salto = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    version_estandar = models.CharField(max_length=10)
    medidas = models.JSONField(null=True)

    class Meta:
        managed = False
        db_table = "repeticiones_analisis"
        ordering = ["numero"]
