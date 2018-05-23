Módulos que permiten generar DTE con OpenERP y LibreDTE.

mc_dte_base: """Este módulo permite consumir servicios de un
servidor de LibreDTE y generar documentos tributarios electrónicos
(33, 34, 56, 61) que están de acuerdo a la normativa del servicio de
impuestos internos de Chile desde un servidor de OpenERP 7. En si, este
módulo sólo hace uso de la API REST y el SDK que están disponibles a
través del mismo proyecto LibreDTE (http://libredte.github.io/
https://github.com/LibreDTE). Deben estar instalados los módulos request
y bs4 para python 2.7 (python-requests python-bs4). Requiere además la 
versión de report_webkit disponible en https://github.com/mallconnectionorg/openerp"""

mc_dte_boleta: """Este módulo permite consumir servicios de un
servidor de LibreDTE y generar documentos tributarios electrónicos
(39 y 41) que están de acuerdo a la normativa del servicio de
impuestos internos de Chile desde un servidor de OpenERP 7. En si, este
módulo sólo hace uso de la API REST y el SDK que están disponibles a
través del mismo proyecto LibreDTE (http://libredte.github.io/
https://github.com/LibreDTE). Deben estar instalados los módulos request
y bs4 para python 2.7 (python-requests python-bs4). Requiere además la 
versión de report_webkit disponible en https://github.com/mallconnectionorg/openerp"""

mc_dte_guia: """Este módulo permite consumir servicios de un
servidor de LibreDTE y generar documentos tributarios electrónicos
(52) que están de acuerdo a la normativa del servicio de
impuestos internos de Chile desde un servidor de OpenERP 7. En si, este
módulo sólo hace uso de la API REST y el SDK que están disponibles a
través del mismo proyecto LibreDTE (http://libredte.github.io/
https://github.com/LibreDTE). Deben estar instalados los módulos request
y bs4 para python 2.7 (python-requests python-bs4). Requiere además la 
versión de report_webkit disponible en https://github.com/mallconnectionorg/openerp"""
