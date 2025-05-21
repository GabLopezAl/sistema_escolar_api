from django.shortcuts import render
from django.db.models import *
from django.db import transaction
from sistema_escolar_api.serializers import *
from sistema_escolar_api.models import *
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.generics import CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.utils.html import strip_tags
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
import string
import random
import json

class EventoAll(generics.CreateAPIView):
    # # Esta función es esencial para todo donde se requiera autorización de incio de sesión (token)
    # permission_classes = (permissions.IsAuthenticated,)
    # def get(self, request, *args, **kwargs):
    #     evento = Eventos.objects.order_by("id")
    #     lista = EventoSerializer(evento, many=True).data

    #     return Response(lista, 200)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        rol = request.query_params.get('rol', '')

        if rol == 'maestro':
            eventos = Eventos.objects.filter(publicoObjetivo__in=['Profesores', 'Público general', 'Profesores, Público general', 'Estudiantes, Profesores', 'Estudiantes, Profesores, Público general']).order_by("id")
        elif rol == 'alumno':
            eventos = Eventos.objects.filter(publicoObjetivo__in=['Estudiantes', 'Público general', 'Estudiantes, Público general', 'Estudiantes, Profesores', 'Estudiantes, Profesores, Público general']).order_by("id")
        else:
            eventos = Eventos.objects.order_by("id")

        lista = EventoSerializer(eventos, many=True).data
        return Response(lista, 200)

class EventoView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)  # Requiere autenticación

    def get(self, request, *args, **kwargs):
        evento = get_object_or_404(Eventos, id=request.GET.get("id"))
        data = EventoSerializer(evento).data
        return Response(data, 200)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = EventoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"evento_creado_id": serializer.data["id"]}, status=201)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class EventoViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,) 

    #def get(self, request, *args, **kwargs):

    def put(self, request,id,*args, **kwargs):
        print("EDITANDO EVENTO ID:", id)
        print("DATOS RECIBIDOS:", request.data)
        evento = get_object_or_404(Eventos, id=id)
        evento.nombre = request.data["nombre"]
        evento.tipoEvento = request.data["tipoEvento"]  
        evento.fecha_realizacion = request.data["fecha_realizacion"]
        evento.horaInicio = request.data["horaInicio"]
        evento.horaFin = request.data["horaFin"]
        evento.lugar = request.data["lugar"]
        evento.publicoObjetivo = request.data["publicoObjetivo"]
        evento.programaEducativo = request.data["programaEducativo"]
        evento.responsable = request.data["responsable"]
        evento.descripcion = request.data["descripcion"]
        evento.cupoMaximo = request.data["cupoMaximo"]
        print("ANTES:", request.data)
        evento.save()
        print("DESPUÉS:", request.data)

        user = EventoSerializer(evento, many=False).data

        return Response(user,200)

    def delete(self, request, *args, **kwargs):
        evento = get_object_or_404(Eventos, id=request.GET.get("id"))
        try:
            evento.delete()
            return Response({"mensaje": "Evento eliminado"}, status=status.HTTP_204_NO_CONTENT)
        except Eventos.DoesNotExist:
            return Response({"error": "Evento no encontrado"}, status=status.HTTP_404_NOT_FOUND)

class AdminAll(generics.CreateAPIView):
    # Esta función es esencial para todo donde se requiera autorización de incio de sesión (token)
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        admin = Administradores.objects.filter(user__is_active = 1).order_by("id")
        lista = AdminSerializer(admin, many=True).data

        return Response(lista, 200)

class AdminView(generics.CreateAPIView):

    def get(self, request, *args, **kwargs):
        admin = get_object_or_404(Administradores, id = request.GET.get("id"))
        admin = AdminSerializer(admin, many=False).data

        return Response(admin, 200)

    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user = UserSerializer(data=request.data)
        if user.is_valid():
            #Grab user data
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            #Valida si existe el usuario o bien el email registrado
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message":"Username "+email+", is already taken"},400)

            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)


            user.save()
            user.set_password(password) #Cifrar la contraseña
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            #Almacenar los datos adicionales del administrador
            admin = Administradores.objects.create(user=user,
                                            clave_admin= request.data["clave_admin"],
                                            telefono= request.data["telefono"],
                                            rfc= request.data["rfc"].upper(),
                                            edad= request.data["edad"],
                                            ocupacion= request.data["ocupacion"])
            admin.save()

            return Response({"admin_created_id": admin.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)

class AlumnosAll(generics.CreateAPIView):
    # Esta función es esencial para todo donde se requiera autorización de incio de sesión (token)
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        alumnos = Alumnos.objects.filter(user__is_active = 1).order_by("id")
        lista = AlumnoSerializer(alumnos, many=True).data

        return Response(lista, 200)

class AlumnoView(generics.CreateAPIView):

    # permission_classes = (permissions.IsAuthenticated,)
    #Obtener usuario por ID
    def get(self, request, *args, **kwargs):
        alumno = get_object_or_404(Alumnos, id = request.GET.get("id"))
        alumno = AlumnoSerializer(alumno, many=False).data

        return Response(alumno, 200)

    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user = UserSerializer(data=request.data)
        if user.is_valid():
            #Grab user data
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            #Valida si existe el usuario o bien el email registrado
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message":"Username "+email+", is already taken"},400)

            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)


            user.save()
            user.set_password(password) #Cifrar la contraseña
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            #Almacenar los datos adicionales del alumno
            alumno = Alumnos.objects.create(user=user,
                                            matricula= request.data["matricula"],
                                            fecha_nacimiento= request.data["fecha_nacimiento"],
                                            curp= request.data["curp"].upper(),
                                            rfc= request.data["rfc"].upper(),
                                            edad= request.data["edad"],
                                            telefono= request.data["telefono"],                                        
                                            ocupacion= request.data["ocupacion"])
            alumno.save()

            return Response({"alumno_created_id": alumno.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)


class MaestrosAll(generics.CreateAPIView):
    # Esta función es esencial para todo donde se requiera autorización de incio de sesión (token)
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        maestros = Maestros.objects.filter(user__is_active = 1).order_by("id")
        maestros = MaestroSerializer(maestros, many=True).data
        # Aqui convertimos los valores de nuevo a un array
        if not maestros:
            return Response({}, 400)
        for maestro in maestros:
            #maestro["materias_json"] = json.loads(maestro["materias_json"])
            materias_raw = maestro.get("materias_json")
            if isinstance(materias_raw, str):
                try:
                    maestro["materias_json"] = json.loads(materias_raw)
                except json.JSONDecodeError:
                    maestro["materias_json"] = []
            elif materias_raw is None:
                maestro["materias_json"] = []
        return Response(maestros, 200)

class MaestroView(generics.CreateAPIView):

    #Obtener usuario por ID
    #permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        maestro = get_object_or_404(Maestros, id = request.GET.get("id"))
        maestro = MaestroSerializer(maestro, many=False).data
        #maestro["materias_json"] = json.loads(maestro["materias_json"])
        materias_raw = maestro.get("materias_json")
        if isinstance(materias_raw, str):
            try:
                maestro["materias_json"] = json.loads(materias_raw)
            except json.JSONDecodeError:
                maestro["materias_json"] = []
        elif materias_raw is None:
            maestro["materias_json"] = []

        return Response(maestro, 200)

    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user = UserSerializer(data=request.data)
        if user.is_valid():
            #Grab user data
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            #Valida si existe el usuario o bien el email registrado
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message":"Username "+email+", is already taken"},400)

            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)


            user.save()
            user.set_password(password) #Cifrar la contraseña
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            #Almacenar los datos adicionales del maestro
            maestro = Maestros.objects.create(user=user,
                                            id_trabajador= request.data["id_trabajador"],
                                            fecha_nacimiento= request.data["fecha_nacimiento"],
                                            telefono= request.data["telefono"],
                                            rfc= request.data["rfc"].upper(),
                                            cubiculo= request.data["cubiculo"],
                                            area_investigacion= request.data["area_investigacion"],
                                            materias_json= json.dumps(request.data["materias_json"]))

            maestro.save()

            return Response({"maestro_created_id": maestro.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
    



class AdminViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,) # Verifica el token de incio de sesión

    def put(self, request, *args, **kwargs):
        admin = get_object_or_404(Administradores, id=request.data["id"])
        admin.clave_admin = request.data["clave_admin"]  
        admin.telefono = request.data["telefono"]
        admin.rfc = request.data["rfc"]
        admin.edad = request.data["edad"]
        admin.ocupacion = request.data["ocupacion"]
        admin.save()
        temp = admin.user
        temp.first_name = request.data["first_name"]  
        temp.last_name = request.data["last_name"]
        temp.save()
        user = AdminSerializer(admin, many=False).data

        return Response(user,200)

    def delete(self, request, *args, **kwargs):
        admin = get_object_or_404(Administradores, id=request.GET.get("id"))
        try:
            admin.user.delete()
            return Response({"details":"Administrador eliminado"},200)
        except Exception as e:
            return Response({"details":"Algo ocurrió al eliminar"},400)
        

class AlumnoViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,) 

    #def get(self, request, *args, **kwargs):

    def put(self, request, *args, **kwargs):
        alumno = get_object_or_404(Alumnos, id=request.data["id"])
        alumno.matricula = request.data["matricula"]  
        alumno.fecha_nacimiento = request.data["fecha_nacimiento"]
        alumno.curp = request.data["curp"]
        alumno.rfc = request.data["rfc"]
        alumno.edad = request.data["edad"]
        alumno.telefono = request.data["telefono"]
        alumno.ocupacion = request.data["ocupacion"]
        alumno.save()
        temp = alumno.user
        temp.first_name = request.data["first_name"]  
        temp.last_name = request.data["last_name"]
        temp.save()
        user = AlumnoSerializer(alumno, many=False).data

        return Response(user,200)

    def delete(self, request, *args, **kwargs):
        alumno = get_object_or_404(Alumnos, id=request.GET.get("id"))
        try:
            alumno.user.delete()
            return Response({"details":"Alumno eliminado"},200)
        except Exception as e:
            return Response({"details":"Algo ocurrió al eliminar"},400)
        


class MaestroViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,) 

    #def get(self, request, *args, **kwargs):

    def put(self, request, *args, **kwargs):
        maestro = get_object_or_404(Maestros, id=request.data["id"])
        maestro.id_trabajador = request.data["id_trabajador"]
        maestro.fecha_nacimiento = request.data["fecha_nacimiento"]  
        maestro.telefono = request.data["telefono"]
        maestro.rfc = request.data["rfc"]
        maestro.cubiculo = request.data["cubiculo"]
        maestro.area_investigacion = request.data["area_investigacion"]
        maestro.materias_json = request.data["materias_json"]
        maestro.save()
        temp = maestro.user
        temp.first_name = request.data["first_name"]  
        temp.last_name = request.data["last_name"]
        temp.save()
        user = MaestroSerializer(maestro, many=False).data

        return Response(user,200)

    def delete(self, request, *args, **kwargs):
        maestro = get_object_or_404(Maestros, id=request.GET.get("id"))
        try:    
            maestro.user.delete()
            return Response({"details":"Maestro eliminado"},200)
        except Exception as e:
            return Response({"details":"Algo ocurrió al eliminar"},400)

class TotalUsuariosPorRolView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        total_admins = Administradores.objects.filter(user__is_active=1).count()
        total_maestros = Maestros.objects.filter(user__is_active=1).count()
        total_alumnos = Alumnos.objects.filter(user__is_active=1).count()

        return Response({
            "total_administradores": total_admins,
            "total_maestros": total_maestros,
            "total_alumnos": total_alumnos
        }, status=200)
