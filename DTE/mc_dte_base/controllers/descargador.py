#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#   DTE Chile OpenERP 7
#   Copyright (C) 2016 Cesar Lopez Aguillon Mall Connection
#   <http://www.mallconnection.org>.
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from web.controllers.main import Export

import web.http as openerpweb

class DescargaXML(Export):
    _cp_path = '/web/binary/descargar_xml'

    def descargar_xml(self, ruta, nombre_archivo):
        ruta_completa = ruta + nombre_archivo + '.xml'
        data = ''
        with open(ruta_completa, 'r') as archivo:
            data = archivo.read()
        return data

    @openerpweb.httprequest
    def index(self, req, ruta, nombre_archivo):
        filename = nombre_archivo + '.xml'
        headers = [
            ('Content-Type', 'application/xml'),
            ('Content-Disposition', 'attachment; filename="' + filename + '"'),
            ('charset', 'utf-8'),
        ]
        if 'RCH' in filename:
            return req.make_response('', headers, cookies=None)
        return req.make_response(self.descargar_xml(ruta, nombre_archivo), headers, cookies=None)

