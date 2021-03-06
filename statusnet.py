# -*- coding: utf-8 *-*
import json
import urllib2
from urllib import urlencode
from base.base import *
from base.multiparte import *
import logging
import socket
import sys
from xml.dom.minidom import parse, parseString

logging.basicConfig()
log = logging.getLogger('StatusNET')
if len(sys.argv) > 1:
    if sys.argv.index('--debug'):
        log.setLevel(logging.DEBUG)


class statusNet():

    dicConeccion = {}
    usuario = ''
    servidor = ''
    clave = ''
    apibase = ''
    mi_perfil = {}
    app_origen = APLICACION_SOURCE
    respuesta_login = ''
    var_conectado = False
    def __init__(self, dicCon):
        self.dicConeccion = dicCon
        self.Configurar()
        self.Conectar()
    
    def Configurar(self):
        self.apibase = self.dicConeccion['servidor'] + "/api"
        self.apibase.replace("//", "/")
        self.servidor = self.dicConeccion['servidor']
        self.usuario = self.dicConeccion['usuario']
        self.clave = self.dicConeccion['clave']

    def Conectar(self):
        pwd_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        pwd_mgr.add_password(None, self.apibase, self.usuario, self.clave)
        self.handler = urllib2.HTTPBasicAuthHandler(pwd_mgr)
        self.opener = urllib2.build_opener(self.handler)
        urllib2.install_opener(self.opener)
        
        try:
            open = urllib2.urlopen(self.apibase + '/account/verify_credentials.json', '', APLICACION_TIEMPO_ESPERA_TIMEOUT)
            leido = open.read()
            self.mi_perfil = json.loads(leido)
            self.var_conectado = True
            self.respuesta_login = '{CredencialValida}'
        except socket.timeout, e2:
            log.debug('El Socket devolvio un TimeOut. Detalle: ' + str(e2))
            self.respuesta_login = '{TimeOut}'
        except urllib2.HTTPError, e1:
            log.debug('Error HTTP: '+ str(e1.code) + str(e1.read()))
            if e1.code == 401:
                self.respuesta_login = '{CredencialInvalida}'
            else:
                self.respuesta_login = '{Error}'
        except urllib2.URLError, e:
            log.debug('Sin respuesta del servidor. Razon: '+ str(e))
            self.respuesta_login = '{TimeOut}'
        except:
            log.debug('Error no identificado')
            self.respuesta_login = '{Error}'


    def EstaConectado(self):
        return self.var_conectado

    def miPerfilAttr(self, param):
        try:
            dato = self.mi_perfil[param]
        except:
            dato = "{Error}"
        return dato

    def Respuestas(self, ultimo=0):
        if ultimo != 0:
            filtro = "?since_id=" + str(ultimo)
        else:
            filtro = ""
        try:
            open = urllib2.urlopen(self.apibase + '/statuses/replies.json' + filtro, '', APLICACION_TIEMPO_ESPERA_TIMEOUT)
            leido = open.read()
            miTL = json.loads(leido)
        except urllib2.URLError, e:
            log.debug('No se pudo contactar al servidor. Razon: ' + str(e))
            miTL = '{TimeOut}'
        except urllib2.HTTPError, e1:
            log.debug('El servidor no pudo procesar la solicitud. Razon: ' + str(e1.code()) + str(e1.reason))
            miTL = '{TimeOut}'
        except socket.timeout, e2:
            log.debug('El Socket devolvio un TimeOut. Detalle: ' + str(e2))
            miTL = '{TimeOut}'
        except:
            log.debug('Error desconocido')
            miTL = '{Error}'
        return miTL

    def Favoritos(self, ultimo=0):
        if ultimo != 0:
            filtro = "?since_id=" + str(ultimo)
        else:
            filtro = ""
        try:
            open = urllib2.urlopen(self.apibase + '/favorites.json' + filtro, '', APLICACION_TIEMPO_ESPERA_TIMEOUT)
            leido = open.read()
            miTL = json.loads(leido)
        except urllib2.URLError, e:
            log.debug('No se pudo contactar al servidor. Razon: ' + str(e))
            miTL = '{TimeOut}'
        except urllib2.HTTPError, e1:
            log.debug('El servidor no pudo procesar la solicitud. Razon: ' + str(e1.code()) + str(e1.reason))
            miTL = '{TimeOut}'
        except socket.timeout, e2:
            log.debug('El Socket devolvio un TimeOut. Detalle: ' + str(e2))
            miTL = '{TimeOut}'
        except:
            log.debug('Error desconocido')
            miTL = '{Error}'
        return miTL

    def TimeLineUser(self):  # Esto hay que ARREGLARLO
        open = urllib2.urlopen(self.apibase + '/statuses/user_timeline.json')
        leido = open.read()
        miTL = json.loads(leido)
        return miTL

    def TimeLineHome(self, ultimo=0):
        if ultimo != 0:
            filtro = "?since_id=" + str(ultimo)
        else:
            filtro = ""
        try:
            open = urllib2.urlopen(self.apibase + '/statuses/home_timeline.json' + filtro, '', APLICACION_TIEMPO_ESPERA_TIMEOUT)
            leido = open.read()
            miTL = json.loads(leido)
        except urllib2.URLError, e:
            log.debug('No se pudo contactar al servidor. Razon: ' + str(e))
            miTL = '{TimeOut}'
        except urllib2.HTTPError, e1:
            log.debug('El servidor no pudo procesar la solicitud. Razon: ' + str(e1.code()) + str(e1.reason))
            miTL = '{TimeOut}'
        except socket.timeout, e2:
            log.debug('El Socket devolvio un TimeOut. Detalle: ' + str(e2))
            miTL = '{TimeOut}'
        except:
            log.debug('Error desconocido')
            miTL = '{Error}'

        return miTL

    def TimeLinePublic(self, ultimo=0):
        if ultimo != 0:
            filtro = "?since_id=" + str(ultimo)
        else:
            filtro = ""
        try:
            open = urllib2.urlopen(self.apibase + '/statuses/public_timeline.json' + filtro, '', APLICACION_TIEMPO_ESPERA_TIMEOUT)
            leido = open.read()
            miTL = json.loads(leido)
        except urllib2.URLError, e:
            log.debug('No se pudo contactar al servidor. Razon: ' + str(e))
            miTL = '{TimeOut}'
        except urllib2.HTTPError, e1:
            log.debug('El servidor no pudo procesar la solicitud. Razon: ' + str(e1.code()) + str(e1.reason))
            miTL = '{TimeOut}'
        except socket.timeout, e2:
            log.debug('El Socket devolvio un TimeOut. Detalle: ' + str(e2))
            miTL = '{TimeOut}'
        except:
            log.debug('Error desconocido')
            miTL = '{Error}'
        return miTL

    def Buzon(self, ultimo=0, param=''):
        param.lower()
        if param != "sent" and param != "new":
            param = ""
        else:
            param = u"/%s" % param
            param.replace("//", "/")
        try:
            open = urllib2.urlopen(self.apibase + '/direct_messages' + param + '.json?since_id=' + str(ultimo), '', APLICACION_TIEMPO_ESPERA_TIMEOUT)
            leido = open.read()
            miTL = json.loads(leido)
        except urllib2.URLError, e:
            log.debug('No se pudo contactar al servidor. Razon: ' + str(e))
            miTL = '{TimeOut}'
        except urllib2.HTTPError, e1:
            log.debug('El servidor no pudo procesar la solicitud. Razon: ' + str(e1.code()) + str(e1.reason))
            miTL = '{TimeOut}'
        except socket.timeout, e2:
            log.debug('El Socket devolvio un TimeOut. Detalle: ' + str(e2))
            miTL = '{TimeOut}'
        except:
            log.debug('Error desconocido')
            miTL = '{Error}'
        return miTL

    def Publicar(self, txt):
        paquete = urlencode({'status': txt, 'source': self.app_origen})
        try:
            open = urllib2.urlopen(self.apibase + '/statuses/update.json?%s' % paquete, '', APLICACION_TIEMPO_ESPERA_TIMEOUT)
            leido = open.read()
            log.debug('Enviado: ' + str(leido))
        except urllib2.URLError, e:
            log.debug('No se pudo contactar al servidor. Razon: ' + str(e))
            leido = '{TimeOut}'
        except urllib2.HTTPError, e1:
            log.debug('El servidor no pudo procesar la solicitud. Razon: ' + str(e1.code()) + str(e1.reason))
            leido = '{TimeOut}'
        except socket.timeout, e2:
            log.debug('El Socket devolvio un TimeOut. Detalle: ' + str(e2))
            leido = '{TimeOut}'
        except:
            log.debug('Error desconocido')
            leido = '{Error}'
        return leido

    def PublicarRespuesta(self, txt, en_respuesta):
        paquete = urlencode({'status': txt, 'source': self.app_origen, 'in_reply_to_status_id': en_respuesta})
        try:
            open = urllib2.urlopen(self.apibase + '/statuses/update.json?%s' % paquete, '', APLICACION_TIEMPO_ESPERA_TIMEOUT)
            leido = open.read()
            log.debug('Enviado: ' + str(leido))
        except urllib2.URLError, e:
            if e.code == 404:
                log.debug('Imposible responder. Posiblemente se elimino el mensaje. Respuesta: ' + str(e))
                leido = '{MensajeBorrado}'
            else:
                log.debug('No se pudo contactar al servidor. Razon: ' + str(e))            
                leido = '{TimeOut}'
        except urllib2.HTTPError, e1:
            log.debug('El servidor no pudo procesar la solicitud. Razon: ' + str(e1.code()) + str(e1.reason))
            leido = '{TimeOut}'
        except socket.timeout, e2:
            log.debug('El Socket devolvio un TimeOut. Detalle: ' + str(e2))
            leido = '{TimeOut}'
        except:
            log.debug('Error desconocido')
            leido = '{Error}'
        return leido


    def Repetir(self, idmensaje):
        try:
            paquete = urlencode({'source': self.app_origen})
            open = urllib2.urlopen(self.apibase + '/statuses/retweet/' + str(idmensaje) + '.json?%s' % paquete, '', APLICACION_TIEMPO_ESPERA_TIMEOUT)
            leido = open.read()
            log.debug('Mensaje repetido: ' + str(leido))
        except urllib2.URLError, e:
            log.debug('No se pudo contactar al servidor. Razon: ' + str(e))
            leido = '{TimeOut}'
        except urllib2.HTTPError, e1:
            log.debug('El servidor no pudo procesar la solicitud. Razon: ' + str(e1.code()) + str(e1.reason))
            leido = '{TimeOut}'
        except socket.timeout, e2:
            log.debug('El Socket devolvio un TimeOut. Detalle: ' + str(e2))
            leido = '{TimeOut}'
        except:
            log.debug('Error desconocido')
            leido = '{Error}'
        return leido

    def Eliminar(self, idmensaje):
        try:
            paquete = urlencode({'source': self.app_origen})
            open = urllib2.urlopen(self.apibase + '/statuses/destroy/' + str(idmensaje) + '.json?%s' % paquete, '', APLICACION_TIEMPO_ESPERA_TIMEOUT)
            leido = open.read()
            log.debug('Mensaje eliminado: ' + str(leido))
        except urllib2.URLError, e:
            log.debug('El mensaje no existe. ' + str(e))
            leido = '{NoExiste}'
        except urllib2.HTTPError, e1:
            log.debug('El servidor no pudo procesar la solicitud. Razon: ' + str(e1.code()) + str(e1.reason))
            leido = '{TimeOut}'
        except socket.timeout, e2:
            log.debug('El Socket devolvio un TimeOut. Detalle: ' + str(e2))
            leido = '{TimeOut}'
        except:
            log.debug('Error desconocido')
            leido = '{Error}'
        return leido

    def Favorito(self, idmensaje, operacion):
        try:
            paquete = urlencode({'source': self.app_origen})
            if operacion == "eliminar":
                api_operacion = "destroy"
            else:
                api_operacion = "create"
            open = urllib2.urlopen(self.apibase + '/favorites/' + api_operacion + '/' + str(idmensaje) + '.json?%s' % paquete, '', APLICACION_TIEMPO_ESPERA_TIMEOUT)
            leido = open.read()
            if api_operacion == "create":
                leido = "{FavoritoCreado}"
                log.debug('Favorito creado: ' + str(leido))
            else:
                leido = "{FavoritoEliminado}"
                log.debug('Favorito eliminado: ' + str(leido))
        except urllib2.URLError, e:
            log.debug('El mensaje no existe. ' + str(e))
            leido = '{NoExiste}'
        except:
            log.debug('Error desconocido')
            leido = '{Error}'
        return leido
    
    def Conversacion(self, conversacion, ultimo=0):
        if ultimo != 0:
            filtro = "?since_id=" + str(ultimo)
        else:
            filtro = ""
        try:
            open = urllib2.urlopen(self.apibase + '/statusnet/conversation/' + conversacion  + '.json' + filtro, '', APLICACION_TIEMPO_ESPERA_TIMEOUT)
            leido = open.read()
            miTL = json.loads(leido)
        except urllib2.URLError, e:
            log.debug('No se pudo contactar al servidor. Razon: ' + str(e))
            miTL = '{TimeOut}'
        except urllib2.HTTPError, e1:
            log.debug('El servidor no pudo procesar la solicitud. Razon: ' + str(e1.code()) + str(e1.reason))
            miTL = '{TimeOut}'
        except socket.timeout, e2:
            log.debug('El Socket devolvio un TimeOut. Detalle: ' + str(e2))
            miTL = '{TimeOut}'
        except:
            log.debug('Error desconocido')
            miTL = '{Error}'
        return miTL

    def Upload(self, ruta):
        content_type, body = encode_multipart_formdata([['media', open(ruta,"rb").read()]])
        headers = {'Content-Type': content_type, 'Content-Length': str(len(body))}
        try:
            req = urllib2.Request(self.apibase + '/statusnet/media/upload', body, headers)
            log.debug('Armando requerimiento')
            respuesta = urllib2.urlopen(req)
            log.debug('Enviando requerimiento')
            strXml = respuesta.read()
            dom = parseString(strXml)
            rsp = dom.getElementsByTagName('rsp')[0]
            stat = rsp.attributes.getNamedItem('stat').value
            if stat == "ok":
                salida = dom.getElementsByTagName('mediaurl')[0].firstChild.data
                log.debug('El Upload devolvio: ok')
            elif stat == "fail":
                log.debug('El Upload devolvio: fail')
                salida = u'Fail||%s' % dom.getElementsByTagName('err')[0].attributes.getNamedItem('msg').value
        except:
            log.debug('El Upload devolvio: Error')
            salida = "{Error}"
        log.debug('UPLOAD - Salida: ' + salida)
        return salida