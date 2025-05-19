from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings

class BearerTokenAuthentication(TokenAuthentication):
    keyword = u"Bearer"


# class Profiles(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
#     creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
#     update = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return "Perfil del usuario "+self.usuario.first_name+" "+self.usuario.last_name

class Administradores(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    clave_admin = models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    rfc = models.CharField(max_length=255, null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    ocupacion = models.CharField(max_length=255, null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Perfil del admin " + self.first_name + " " + self.last_name
    
# Crear dos tablas (alumnos, maestros)

class Alumnos(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    matricula = models.CharField(max_length=255, null=True, blank=True)
    fecha_nacimiento = models.CharField(max_length=255,null=True, blank=True)
    curp = models.CharField(max_length=255, null=True, blank=True)
    rfc = models.CharField(max_length=255, null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    ocupacion = models.CharField(max_length=255, null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Perfil del alumno " + self.first_name + " " + self.last_name

class Maestros(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    id_trabajador = models.CharField(max_length=255, null=True, blank=True)
    fecha_nacimiento = models.CharField(max_length=255,null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    rfc = models.CharField(max_length=255, null=True, blank=True)
    cubiculo = models.IntegerField(null=True, blank=True)
    area_investigacion = models.CharField(max_length=255, null=True, blank=True)
    materias_json = models.TextField(null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Perfil del maestro " + self.first_name + " " + self.last_name


class Eventos(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('Conferencia', 'Conferencia'),
        ('Taller', 'Taller'),
        ('Seminario', 'Seminario'),
        ('Concurso', 'Concurso'),
    ]
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    tipoEvento = models.CharField("Tipo de evento", max_length=50, choices=TIPO_EVENTO_CHOICES)
    fecha_realizacion = models.DateField()
    horaInicio = models.TimeField()
    horaFin = models.TimeField()
    lugar = models.CharField(max_length=150)
    publicoObjetivo = models.CharField("Publico Objetivo", max_length=255,default="")
    programaEducativo = models.CharField(max_length=100, blank=True, null=True)
    responsable = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=300)
    cupoMaximo = models.PositiveIntegerField()

    def __str__(self):
        return self.nombre

