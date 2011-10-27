﻿# -*- coding: utf-8 *-*
import wx
import wx.html
import wx.animate
from wx.lib.wordwrap import wordwrap
import threading
from wx.lib.pubsub import Publisher
import httplib
import sys
import os
import datetime
import time
import getpass
import logging
import re
from statusnet import *

logging.basicConfig()
log = logging.getLogger('GUI')
log.setLevel(logging.DEBUG)

class InterfazPrincipal(wx.Frame):
    cols = []
    #
    ultimo = 0
    red = None
    txt = ''
    timer = None  # El timer de actualizar
    dir_perfiles = './perfiles/'
    dir_usuario = ''
    dir_imagenes = ''
    app_dir_img = './img/'
    color_tab_1 = "#FFFFFF"
    color_tab_2 = "#E6F8E0"
    color_tab = ""
    usuario = ''
    clave = ''
    servidor = ''
    intervaloTL = 15
    txtDescripcion = ''
    me = None #Variable con datos del usuario, no implementada aun
    primeraCargaImg = True
    #
    def __init__(self, parent, titulo, servidor, usuario, clave):
        self.parent = parent
        self.usuario = usuario
        self.clave = clave
        self.servidor = servidor
        wx.Frame.__init__(self, parent, wx.ID_ANY, titulo, size=(700, 600))
        self.Conectar(self.servidor, self.usuario, self.clave)

    def __del__(self):
        try:
            self.timer.cancel()
        except:
            pass
        log.debug('Terminando Aplicacion')
        self.parent.Destroy()

    def Conectar(self, servidor, usuario, clave):
        log.debug('Creando Coneccion')
        self.red = statusNet(servidor, usuario, clave)
        if self.red.estaConectado():
            log.debug('Se establecio la Coneccion')
            self.VerificarDirectorios()
            self.ConfigurarVentana()
            self.Actualizar()

    def EnterEstado(self, event):
        self.EnviarMensaje()

    def BotonEstado(self, event):
        self.EnviarMensaje()

    def EnviarMensaje(self):
        texto = self.txt_estado.GetValue()
        texto = texto.encode('utf8')
        texto = texto.strip()
        #texto = ''
        if texto != '':
            res = self.red.Publicar(texto)
            if res != "{Error}":
                self.txt_estado.Clear()
            else:
                #Aqui deberia enviarse un mensaje de envio fallido
                wx.MessageBox(u'Su mensaje no pudo ser enviado =(', 'Aviso')
                pass
        else:
            wx.MessageBox('Debe ingresar un mensaje')

    def RutaOnlineToLocal(self, ruta):
        img_arr = ruta.split("/")
        img_nombre = img_arr[len(img_arr) - 1]
        if (os.path.isfile(self.dir_imagenes + img_nombre)):
            img_ruta_local = self.dir_imagenes + img_nombre
        else:
            img_ruta_local = self.app_dir_img + 'default.png'
        return img_ruta_local

    def DescargarAvatar(self, ruta_img):
        tmp = ruta_img.split("/")
        img_nombre = tmp[len(tmp) - 1]
        img_ruta = "/avatar/" + img_nombre
        img_ruta_local = self.dir_imagenes + img_nombre
        tmp_serv = self.red.servidor.split("//")
        serv = "www." + tmp_serv[1]
        tmp2 = img_nombre.split('-')
        idu = tmp2[0] #esto es el ID del usuario, antes del primer guion
        if (not os.path.isfile(img_ruta_local)):
            if self.primeraCargaImg:
                log.debug('Intentando eliminar la imagen antigua')
                try:
                    self.BorrarImgAnterior(idu)
                except:
                    log.debug('No se encontro la imagen o no se pudo borrar')
            # Descargando nueva imagen
            try:
                con = httplib.HTTPConnection(serv)
                con.request("GET", img_ruta)
                r = con.getresponse()
                archivo = file(img_ruta_local, 'wb')
                archivo.write(r.read())
                archivo.close()
                log.debug("Imagen descargada")
            except:
                log.debug("Error al descargar imagen")
        else:
            log.debug('Ya existe la imagen')

    def BorrarImgAnterior(self, idusuario):
        ficheros = os.listdir(self.dir_imagenes)
        for nombreA in ficheros:
            if (re.search('^'+ idusuario +'-', nombreA)):
                os.remove(self.dir_imagenes + nombreA)
                log.debug('Se borro la imagen anterior')

    def InnerHTML(self, txt):
        log.debug("Inyectando HTML")
        self.cols[0].SetPage(txt)
        log.debug("Finalizando Inyeccion HTML")

    def ActualizaBarraEstado(self):
        origen = self.cols[0].GetOrigen()
        Lugar = 'No definido'
        if origen == 'tl_home':
            Lugar = 'Inicio'
        if origen == 'tl_public':
            Lugar = u'Público'
        if origen == 'replies':
            Lugar = 'Respuestas'
        if origen == 'favorites':
            Lugar = 'Favoritos'
        self.sBar.SetFields((Lugar,'Otra Info...'))

    def Actualizar(self):
        self.ActualizaBarraEstado()
        log.debug("Intentando Actualizar " + self.cols[0].GetOrigen())
        if self.red.estaConectado():
            log.debug("Solicitando Datos del Servidor")
            if self.cols[0].origen == 'tl_home':
                mitl = self.red.TimeLineHome(self.ultimo)
            if self.cols[0].origen == 'tl_public':
                mitl = self.red.TimeLinePublic(self.ultimo)
            if self.cols[0].origen == 'replies':
                mitl = self.red.Respuestas(self.ultimo)
            if self.cols[0].origen == 'favorites':
                mitl = self.red.Favoritos(self.ultimo)
            tmp = ''
            ultimo = 0
            cont = 0

            if len(mitl) > 0:
                log.debug("Se recibieron mensajes nuevos")
                log.debug("Parseando los datos")
                #tmp = tmp + "<hr size=\"2\">"
                for tl in mitl:
                    if self.color_tab != self.color_tab_1:
                        self.color_tab = self.color_tab_1
                    else:
                        self.color_tab = self.color_tab_2
                    #self.color_tab = '#FFFFFF' #BORRAR ESTO ############
                    cont = cont + 1
                    self.DescargarAvatar(tl['user']['profile_image_url'])
                    img_tmp = tl['user']['profile_image_url']
                    img_arr = img_tmp.split("/")
                    img_nombre = img_arr[len(img_arr) - 1]
                    if (os.path.isfile(self.dir_imagenes + img_nombre)):
                        img_ruta_local = self.dir_imagenes + img_nombre
                    else:
                        img_ruta_local = self.app_dir_img + 'default.png'
                    tmp = tmp + '<table bgcolor="' + self.color_tab + '" width="100%" border="0"><tr><td width="48" valign="top"><img align="left" src="' + img_ruta_local + '"></td><td valign="top">'
                    tmp = tmp + '<font size="2"><b>' + tl['user']['screen_name'] + '</b><br>'
                    #fecha = datetime.datetime.strptime(tl['created_at'], "%A %b %d %H:%M:%S %Z %Y")
                    #ya = datetime.date.today()
                    #f1_d = int(fecha.strftime('%d'))
                    #f1_m = int(fecha.strftime('%m'))
                    #f1_Y = int(fecha.strftime('%Y'))
                    #f2_d = int(ya.strftime('%d'))
                    #f2_m = int(ya.strftime('%m'))
                    #f2_Y = int(ya.strftime('%Y'))
                    #tm = f2_m - f1_m
                    strfecha = ""
                    #strfecha = "%s minutos" % (str(tm))
                    if tl['in_reply_to_user_id'] != None:
                        en_respuesta = "En respuesta a <i>" + tl['in_reply_to_screen_name'] + "</i>"
                    else:
                        en_respuesta = ''
                    fila_info = '<br><font size="1" color="gray">%s</font>' % en_respuesta
                    tmp = u"%s %s</font>%s</td></tr></table>" % (tmp, tl['text'],fila_info) #text o statusnet_html
                    if cont < len(mitl):
                        #tmp = tmp + "<br><br>"
                        pass
                    if ultimo == 0:
                        ultimo = tl['id']
                        self.ultimo = ultimo
                log.debug("Finalizando descarga de mensajes")
                self.txt = tmp + self.txt
                self.InnerHTML(self.txt)
            else:
                log.debug("No existen mensajes nuevos")

            log.debug("ID de ultimo mensaje recibido: %s" % str(self.ultimo))
            #Intentando crear timer
            if self.timer == None:
                self.timer = threading.Timer(self.intervaloTL, self.Actualizar)
                log.debug("Creando timer a %s segundos", str(self.intervaloTL))
            else:
                log.debug("Deteniendo el timer")
                self.timer.cancel()
                self.timer = None
                log.debug("Reiniciando timer a %s segundos", str(self.intervaloTL))
                self.timer = threading.Timer(self.intervaloTL, self.Actualizar)
            self.timer.start()
            #La siguiente linea especifica que de ahora en adelante no es la primera carga de imagenes
            if self.primeraCargaImg:
                self.primeraCargaImg = False

    def RedimensionVentana(self, event):
        tamano = self.GetSize()
        ancho = tamano[0] + 100
        texto = wordwrap(self.txtDescripcion, ancho, wx.ClientDC(self))
        self.lblDescripcion.SetLabel(texto)
        #log.debug(texto)
        #log.debug('Ancho: ' + str(ancho))
        event.Skip()

    def ConfigurarVentana(self):
        log.debug('Configurando Ventana')
        icono = wx.Icon('img/iconosolo16.png', wx.BITMAP_TYPE_PNG)
        self.SetIcon(icono)
        self.SetMinSize((400, 500))

        self.panel = wx.Panel(self)

        #self.toolBar = self.CreateToolBar( wx.TB_HORIZONTAL, wx.ID_ANY )
        #self.toolBar.AddLabelTool(wx.ID_ANY, u"Inicio", wx.Bitmap( u"img/home.png", wx.BITMAP_TYPE_ANY ))
        #self.toolBar.Realize()

        #Configurando la fila del perfil de usuario
        self.h_sizerPerfil = wx.BoxSizer(wx.HORIZONTAL)
        ruta_img = self.red.miPerfilAttr('profile_image_url')
        ruta_img_local = self.RutaOnlineToLocal(ruta_img)
        self.DescargarAvatar(ruta_img)
        self.miImagen = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(ruta_img_local, wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.h_sizerPerfil.Add(self.miImagen, 0, wx.TOP|wx.LEFT|wx.RIGHT, 5 )

        self.v_sizerInfo = wx.BoxSizer(wx.VERTICAL)

        usr_nombre = self.red.miPerfilAttr('screen_name')
        self.lblUsuario = wx.StaticText(self.panel, wx.ID_ANY, usr_nombre, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lblUsuario.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
        self.lblUsuario.Wrap(-1)

        self.txtDescripcion = self.red.miPerfilAttr('description')
        usr_descripcion = ''
        self.lblDescripcion = wx.StaticText(self.panel, wx.ID_ANY, usr_descripcion, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lblDescripcion.SetFont( wx.Font(7, 70, 90, wx.NORMAL, False, wx.EmptyString ) )
        #self.lblDescripcion.Wrap(1)
        #self.lblDescripcion.Wrap(320)
        #
        self.v_sizerInfo.Add(self.lblUsuario, 0, wx.TOP|wx.LEFT, 5 )
        self.v_sizerInfo.Add(self.lblDescripcion, 1, wx.EXPAND|wx.BOTTOM|wx.LEFT, 5 )

        self.h_sizerPerfil.Add(self.v_sizerInfo, 0, wx.ALL|wx.EXPAND, 0 )

        #configurando la fila de estado
        self.h_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        #self.etiqueta = wx.StaticText(self.panel, wx.ID_ANY, 'Estado: ')
        #self.h_sizer1.Add(self.etiqueta, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        self.txt_estado = wx.TextCtrl(self.panel, wx.ID_ANY, '', (-1, -1), (-1, 50), style=wx.TE_MULTILINE|wx.TE_NO_VSCROLL)
        self.h_sizer1.Add(self.txt_estado, 1, wx.ALL|wx.EXPAND, 5)
        self.btn_aceptar = wx.BitmapButton(self.panel, wx.ID_ANY, wx.Bitmap( u"img/aceptar.png", wx.BITMAP_TYPE_ANY ), pos=wx.DefaultPosition, size=(40,25), style=wx.BU_AUTODRAW )
        self.h_sizer1.Add(self.btn_aceptar, 0, wx.ALL, 5)

        #Configurando eventos
        self.panel.Bind(wx.EVT_BUTTON, self.BotonEstado, self.btn_aceptar)
        self.panel.Bind(wx.EVT_TEXT_ENTER, self.EnterEstado, self.txt_estado)
        self.Bind(wx.EVT_SIZE, self.RedimensionVentana)

        #Barra de Herramientas
        self.h_sizerBarra = wx.BoxSizer(wx.HORIZONTAL)
        btn_tam = wx.Size(40,40)
        self.btnInicio = wx.BitmapButton(self.panel, wx.ID_ANY, wx.Bitmap( u"img/inicio24x24.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, btn_tam, wx.BU_AUTODRAW)
        self.btnInicio.SetToolTipString( u"Inicio" )
        self.btnPublico = wx.BitmapButton(self.panel, wx.ID_ANY, wx.Bitmap( u"img/publico24x24.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, btn_tam, wx.BU_AUTODRAW)
        self.btnPublico.SetToolTipString( u"Público" )
        self.btnRespuestas = wx.BitmapButton(self.panel, wx.ID_ANY, wx.Bitmap( u"img/respuestas24x24.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, btn_tam, wx.BU_AUTODRAW)
        self.btnRespuestas.SetToolTipString( u"Respuestas" )
        self.btnMensajes = wx.BitmapButton(self.panel, wx.ID_ANY, wx.Bitmap( u"img/dm24x24.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, btn_tam, wx.BU_AUTODRAW)
        self.btnMensajes.SetToolTipString( u"Mensajes (Aun no implementado)" )
        self.btnFavoritos = wx.BitmapButton(self.panel, wx.ID_ANY, wx.Bitmap( u"img/favoritos24x24.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, btn_tam, wx.BU_AUTODRAW)
        self.btnFavoritos.SetToolTipString( u"Favoritos" )
        self.h_sizerBarra.Add(self.btnInicio, 0, wx.BOTTOM|wx.LEFT, 5)
        self.h_sizerBarra.Add(self.btnPublico, 0, wx.BOTTOM, 5)
        self.h_sizerBarra.Add(self.btnRespuestas, 0, wx.BOTTOM, 5)
        self.h_sizerBarra.Add(self.btnFavoritos, 0, wx.BOTTOM, 5)
        self.h_sizerBarra.Add(self.btnMensajes, 0, wx.BOTTOM, 5)
        #
        self.Bind(wx.EVT_BUTTON, self.CambioLinea, self.btnPublico)
        self.Bind(wx.EVT_BUTTON, self.CambioLinea, self.btnInicio)
        self.Bind(wx.EVT_BUTTON, self.CambioLinea, self.btnRespuestas)
        self.Bind(wx.EVT_BUTTON, self.CambioLinea, self.btnFavoritos)


        self.h_sizer2 = wx.BoxSizer(wx.HORIZONTAL)

        self.cols.append(self.NuevaColumna('tl_home'))
        self.v_sizer = wx.BoxSizer(wx.VERTICAL)

        #Se agregan los Sizers horizontales al Sizer Vertical Principal
        self.v_sizer.Add(self.h_sizerPerfil, 0, wx.EXPAND|wx.ALL, 0)
        self.v_sizer.Add(self.h_sizer1, 0, wx.EXPAND|wx.ALL, 0)
        self.v_sizer.Add(self.h_sizerBarra, 0, 0, 0) #Sizer Barra
        self.v_sizer.Add(self.h_sizer2, 1, wx.EXPAND|wx.ALL, 0)
        self.panel.SetSizer(self.v_sizer)
        self.sBar = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
        self.txt_estado.SetFocus()
        log.debug('Ventana Configurada')
        log.debug('Cerrando Ventana de Login')
        self.Centre(wx.BOTH)
        self.Show()
        self.parent.Hide()

    def CambioLinea(self, event):
        obj = event.GetEventObject()
        origen_ant = self.cols[0].GetOrigen()
        if obj == self.btnInicio:
            if origen_ant == 'tl_home':
                return False
            self.cols[0].SetOrigen('tl_home')
        if obj == self.btnPublico:
            if origen_ant == 'tl_public':
                return False
            self.cols[0].SetOrigen('tl_public')
        if obj == self.btnRespuestas:
            if origen_ant == 'replies':
                return False
            self.cols[0].SetOrigen('replies')
        if obj == self.btnFavoritos:
            if origen_ant == 'favorites':
                return False
            self.cols[0].SetOrigen('favorites')
        log.debug('Cambio de Linea de Tiempo')
        self.txt = ''
        self.ultimo = 0

        self.InnerHTML(self.txt)
        try:
            self.timer.cancel()
            self.timer = None
            log.debug('Se detuvo el Timer')
        except:
            log.debug('Error al intentar detener Timer')
        self.Actualizar()


    def NuevaColumna(self, origen):
        col = cColumna(self.panel, origen)
        self.h_sizer2.Add(col, 1, wx.EXPAND | wx.ALL, 0)
        log.debug('Se agrego una colmuna')
        return col

    def VerificarDirectorios(self):
        log.debug('Verificando si existen los directorios')
        self.dir_usuario = self.dir_perfiles + str(self.red.miPerfilAttr('id'))
        self.dir_imagenes = self.dir_usuario + '/imagenes/'
        if (not os.path.isdir(self.dir_perfiles)):
            os.makedirs(self.dir_imagenes)
            log.debug('Se crearon las carpetas Perfiles, Usuario, Imagenes')
        if (not os.path.isdir(self.dir_usuario)):
            os.mkdir(self.dir_usuario)
            log.debug('Se creo la carpeta Perfil')
        if (not os.path.isdir(self.dir_imagenes)):
            os.mkdir(self.dir_imagenes)
            log.debug('Se creo la carpeta Imagenes')


class cColumna(wx.html.HtmlWindow):

    origen = ''
    intervalo = 0

    def __init__(self, parent, origen, intervalo=15):
        wx.html.HtmlWindow.__init__(self, parent)
        self.SetMinSize((200, -1))
        self.SetBorders(0)
        self.origen = origen
        self.intervalo = intervalo

    def SetOrigen(self, orig):
        self.origen = orig

    def GetOrigen(self):
        return self.origen


class PlaxedLogin(wx.Frame):
    Validado = False
    usr = ''
    pas = ''
    serv = ''
    def __init__(self, parent):
        self.parent = parent
        wx.Frame.__init__(self, None, wx.ID_ANY, 'Plaxed Desktop (Demo)', size=(320, 450))
        self.ConfigurarVentana()

    def ConfigurarVentana(self):
        log.debug('Configurando Ventana')
        icono = wx.Icon('img/iconosolo16.png', wx.BITMAP_TYPE_PNG)
        self.SetIcon(icono)
        self.SetMinSize((320, 450))
        self.panel = wx.Panel(self)
        self.bsizer = wx.BoxSizer(wx.VERTICAL)
        self.txt_usuario = wx.TextCtrl(self.panel, wx.ID_ANY, '', size=(160, -1))
        self.txt_usuario.SetFocus()
        self.txt_usuario.SetMaxLength(15)
        self.txt_clave = wx.TextCtrl(self.panel, wx.ID_ANY, '', size=(160, -1), style=wx.TE_PASSWORD)
        self.txt_clave.SetMaxLength(15)
        self.boton = wx.Button(self.panel, wx.ID_ANY, 'Ingresar')
        self.imagen = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap( u"img/iconosolo64.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )

        self.lbl_usuario = wx.StaticText(self.panel, wx.ID_ANY, u"Usuario:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_usuario.Wrap( -1 )
        self.lbl_clave = wx.StaticText(self.panel, wx.ID_ANY, u"Clave:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.lbl_clave.Wrap( -1 )
        #bSizer4.Add( self.m_staticText1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

        self.bsizer.Add(self.imagen, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 30)
        self.bsizer.Add(self.lbl_usuario, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.bsizer.Add(self.txt_usuario, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.bsizer.Add(self.lbl_clave, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.bsizer.Add(self.txt_clave, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.bsizer.Add(self.boton, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 30)

        #Agregar un Loader: Test()
        self.ag_fname = "img/loader.gif"
        self.ag = wx.animate.GIFAnimationCtrl(self.panel, -1, self.ag_fname, pos=(-1, -1))
        self.bsizer.Add(self.ag, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 0)
        # clears the background
        self.ag.GetPlayer().UseBackgroundColour(False)
        
        
        #self.SetSizer(self.bsizer)
        self.panel.SetSizer(self.bsizer)
        self.Bind(wx.EVT_BUTTON, self.Entrar, self.boton)
        self.sBar = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
        self.Centre(wx.BOTH)
        log.debug('Ventana Configurada')
        self.Show()

    def Conectar(self, servidor, usuario, clave):
        log.debug('Verificando Sesion')
        #self.PlayLoader() #Esto deberia ser en un hilo
        self.red = statusNet(servidor, usuario, clave)
        if self.red.estaConectado():
            log.debug('Credenciales Validas')
            self.Validado = True
        else:
            log.debug('Credenciales Invalidas')

    def PlayLoader(self):
        self.ag.Play()
    
    def StopLoader(self):
        self.ag.Stop()

    def Entrar(self, event):
        self.sBar.SetStatusText('Examinando los datos...')
        self.txt_usuario.Disable()
        self.txt_clave.Disable()
        usuario = self.txt_usuario.GetValue()
        usuario = usuario.strip()
        clave = self.txt_clave.GetValue()
        clave = clave.strip()
        #
        if usuario == "" or clave == "":
            wx.MessageBox(u'Debe ingresar sus datos (usuario/clave)...')
            self.sBar.SetStatusText('')
            self.txt_usuario.Enable()
            self.txt_clave.Enable()
            return False
        self.boton.Disable()
        servidor = 'http://beta.plaxed.com'
        self.usuario = usuario
        self.clave = clave
        self.servidor = servidor
        self.PlayLoader()
        Publisher().subscribe(self.LoginCorrecto, "LoginAceptado")
        Publisher().subscribe(self.LoginFallido, "LoginRechazado")
        self.sBar.SetStatusText('Validando credenciales...')
        self.t = HiloValidar(self, self.servidor, self.usuario, self.clave)
    
    def LoginCorrecto(self, msj):
        log.debug('Accesando a Interfaz Principal')
        self.sBar.SetStatusText(u'Cargando Aplicación...')
        frmMain = InterfazPrincipal(self, "Plaxed Desktop (Demo)", self.servidor, self.usuario, self.clave)
    
    def LoginFallido(self, msj):
        log.debug('Error de Autenticacion')
        self.StopLoader()
        self.sBar.SetStatusText(u'Error de Autenticación...')
        self.txt_usuario.Enable()
        self.txt_clave.Enable()
        self.txt_usuario.SetFocus()    
        self.boton.Enable()

    def __del__(self):
        try:
            frmMain.Destroy()
        except:
            pass

class HiloValidar(threading.Thread):
    servidor = ''
    usuario = ''
    clave = ''
    parent = None
    def __init__(self, parent, servidor, usuario, clave):
        threading.Thread.__init__(self)
        self.parent = parent
        self.servidor=servidor
        self.clave=clave
        self.usuario=usuario
        self.start()
        
    def run(self):
        self.red = statusNet(self.servidor, self.usuario, self.clave)
        if self.red.estaConectado():
            wx.CallAfter(Publisher().sendMessage, "LoginAceptado", "Thread finished!")
        else:
            wx.CallAfter(Publisher().sendMessage, "LoginRechazado", "Thread finished!")
        
        


class PlaxedApp(wx.App):
    usuario = ''
    clave = ''
    servidor = ''
    frmMain = None

    def __init__(self):
        wx.App.__init__(self, True)
        self.frmLogin = PlaxedLogin(self)
        self.MainLoop()
