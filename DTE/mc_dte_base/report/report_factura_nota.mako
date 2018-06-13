<html>
<head>
    <style type="text/css">
        ${css}
        pre {font-family:helvetica; font-size:12;}
    </style>
</head>

<body>
    <%
    def carriage_returns(text):
        return text.replace('\n', '<br />')
    %>

    %for inv in objects:
    <% 
    setLang(inv.partner_id.lang)
    dicc_impresion = dicc_imp(inv) 
    %>
    
        %for copia in ('', 'CEDIBLE'):

    <table width="100%" cellspacing="0" cellpadding="0" height="100%" border="0" style="padding-top: 50px;">
        <tbody>
            <tr height="10%">
                <td>
                    <table style="border-collapse: collapse;" border="0">
                        <tbody>
                            <tr>
                                <td style="vertical-align: top;" align="left">
                                    <table style="border-collapse: collapse;" width="100%" height="100%" border="0">
                                        <tbody>
                                            <tr>
                                                <td class="emisor_1">${dicc_impresion['emisor_rs']}</td>
                                            </tr>
                                            <tr>
                                                <td class="emisor_2">GIRO:&nbsp;${dicc_impresion['emisor_giro']}</td>
                                            </tr>
                                            <tr>
                                                <td class="emisor_3">CASA MATRIZ:&nbsp;${dicc_impresion['emisor_cm']}</td>
                                            </tr>
                                            <tr>
                                                <td class="emisor_3">SUCURSAL:&nbsp;${dicc_impresion['emisor_suc']}</td>
                                            </tr>
                                            <tr>
                                                <td class="emisor_3">CONTACTO:&nbsp;${dicc_impresion['emisor_cont']}</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </td>
                                <td width="30%" align="right">
                                    <table style="border-collapse: collapse;" width="370pt" align="right" height="210pt" border="0">
                                        <tbody>
                                            <tr align="right" height="90%">
                                                <td class="recuadro_sii">R.U.T.: ${dicc_impresion['emisor_rut']}<br>
                                                                        ${dicc_impresion['tipo_doc']}<br>
                                                                        <br>
                                                                        N° ${dicc_impresion['folio']}<br>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="color: red;font-size: 12pt;" align="center">S.I.I. - ${dicc_impresion['oficina_sii']}</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </td>
            </tr>
            <tr>
                <td>
                    <table class="cliente" style="border-collapse: collapse;" width="100%">
                        <tbody>
                            <tr>
                                <td style="font-size: 8pt;"><br></td>
                            </tr>
                            <tr>
                                <td align="right"><b>${dicc_impresion['fecha_texto']}</b></td>
                            </tr>
                        </tbody>
                    </table>
                    <table style="border: 1px solid rgb(0, 0, 0) !important;" class="cliente" width="100%">
                        <tbody>
                            <tr>
                                <td align="left"><b>Razón social:</b>&nbsp;${dicc_impresion['receptor_rs']}</td>
                                <td width="30%"><b>R.U.T:</b>&nbsp;${dicc_impresion['receptor_rut']}</td>
                            </tr>
                            <tr>
                                <td colspan="2"><b>Giro:</b>&nbsp;${dicc_impresion['receptor_giro']}</td>
                            </tr>
                            <tr>
                                <td colspan="2"><b>Dirección:</b>&nbsp;${dicc_impresion['receptor_direccion']}</td>
                            </tr>
                            <tr>
                                <td><b>Comuna:</b>&nbsp;${dicc_impresion['receptor_comuna']}</td>
                                <td width="30%"><b>Pago:</b>&nbsp;${dicc_impresion['cond_pago']}</td>
                            </tr>
                        </tbody>
                    </table>
                </td>
            </tr>
            <tr>
                <td><br></td>
            </tr>
            <tr>
                <td>
                    <table class="tabla_encabezado_detalle" width="100%">
                        <tbody>
                            <tr>
                                <td width="15%">Código</td>
                                <td>Descripción</td>
                                <td width="6%" align="center">Cant.</td>
                                <td width="4%" align="center">Unid.</td>
                                <td width="10%" align="center">P. Unit.</td>
                                <td width="10%" align="center">$ Dscto.</td>
                                <td width="10%" align="right">Valor</td>
                            </tr>
                        </tbody>
                    </table>
                </td>
            </tr>
            <tr>
                <td>
                    <table class="tabla_detalle" width="100%">
                        <tbody>
                        <!-- AQUI DEBE IR UN FOR PARA LAS LINEAS DEL DETALLE -->
                        %for linea_detalle in dicc_impresion['detalle']:
                            <tr>
                                <td width="15%">${linea_detalle['codigo']}</td>
                                %if not linea_detalle['descripcion']:
                                    <td>${linea_detalle['nombre']}</td>
                                %else:
                                    <td>${linea_detalle['nombre']}<br><p style="font-size: 8pt;">${linea_detalle['descripcion']}</p></td>
                                %endif
                                <td width="6%" align="center">${linea_detalle['cantidad']}</td>
                                <td width="4%" align="center">${linea_detalle['unidad']}</td>
                                <td width="10%" align="center">${linea_detalle['precio_unitario']}</td>
                                <td width="10%" align="center">${linea_detalle['descuento']}</td>
                                <td width="10%" align="right">${linea_detalle['valor']}</td>
                            </tr>
                            
                        %endfor
                        %if dicc_impresion['lineas_detalle_relleno'] > 0:
                            %for i in range(dicc_impresion['lineas_detalle_relleno']):
                                <tr>
                                    <td width="15%"><br></td>
                                    <td><br></td>
                                    <td width="6%" align="center"><br></td>
                                    <td width="4%" align="center"><br></td>
                                    <td width="10%" align="center"><br></td>
                                    <td width="10%" align="center"><br></td>
                                    <td width="10%" align="right"><br></td>
                                </tr>
                            %endfor
                        %endif
                        <!-- AQUI TERMINA EL FOR PARA LAS LINEAS DEL DETALLE -->
                        </tbody>
                    </table>
                </td>
            </tr>
            <tr>
                <td height="100%"><br>
                </td>
            </tr>
            %if dicc_impresion['referencias']:
            <tr>
                <td>
                    <table class="tabla_encabezado_referencias" width="100%">
                        <tbody>
                            <tr>
                                <td colspan="4" align="center">Referencias a otros documentos</td>
                            </tr>
                        </tbody>
                    </table>
                </td>
            </tr>
            <tr>
                <td>
                    <table class="tabla_referencias" width="100%">
                        <tbody>
                            <tr>
                                <td style="border-bottom: 1px solid black;" width="25%" align="center"><b>Tipo documento</b></td>
                                <td style="border-bottom: 1px solid black;" width="15%" align="center"><b>Folio</b></td>
                                <td style="border-bottom: 1px solid black;" width="10%" align="center"><b>Fecha</b></td>
                                <td style="border-bottom: 1px solid black;" align="center"><b>Razón referencia</b></td>
                            </tr>
                            <!-- AQUI DEBE IR UN FOR PARA LAS LINEAS DE LAS REFERENCIAS -->
                            %for linea_referencia in dicc_impresion['referencias']:
                            <tr>
                                <td width="25%" align="center">${linea_referencia['tipo_documento']}</td>
                                <td width="15%" align="center">${linea_referencia['folio_ref']}</td>
                                <td width="10%" align="center">${linea_referencia['fecha_ref']}</td>
                                <td align="center">${linea_referencia['razon_ref']}</td>
                            </tr>
                            %endfor
                            <!-- AQUI TERMINA EL FOR PARA LAS LINEAS DE LAS REFERENCIAS -->
                        </tbody>
                    </table>
                </td>
            </tr>
            <tr>
            <td><br>
            </td>
            </tr>
            %endif
            %if dicc_impresion['comisiones']:
            <tr>
                <td>
                    <table class="tabla_encabezado_comisiones" width="100%">
                        <tbody>
                            <tr>
                                <td colspan="4" align="center">Comisiones y otros cargos</td>
                            </tr>
                        </tbody>
                    </table>
                </td>
            </tr>
            <tr>
                <td>
                    <table class="tabla_comisiones" width="100%">
                        <tbody>
                            <tr>
                                <td style="border-bottom: 1px solid black;" width="67%" align="center"><b>Glosa</b></td>
                                <td style="border-bottom: 1px solid black;" align="center"><b>IVA</b></td>
                                <td style="border-bottom: 1px solid black;" align="center"><b>Neto</b></td>
                                <td style="border-bottom: 1px solid black;" align="center"><b>Exento</b></td>
                            </tr>
                            <!-- AQUI DEBE IR UN FOR PARA LAS LINEAS DE LAS COMISIONES -->
                            %for linea_comision in dicc_impresion['comisiones']['lineas']:
                            <tr>
                                <td width="67%">${linea_comision['glosa']}</td>
                                <td align="center">${linea_comision['iva']}</td>
                                <td align="center">${linea_comision['neto']}</td>
                                <td align="center">${linea_comision['exento']}</td>
                            </tr>
                            %endfor
                            <!-- AQUI TERMINA EL FOR PARA LAS LINEAS DE LAS COMISIONES -->
                            <tr>
                                <% totales_comisiones = dicc_impresion['comisiones']['totales'] %>
                                <td width="67%"><br></td>
                                <td style="border-top: 1px solid black;" align="center">Total:</td>
                                <td style="border-top: 1px solid black;" align="center">${totales_comisiones['suma_neto']}</td>
                                <td style="border-top: 1px solid black;" align="center">${totales_comisiones['suma_exento']}</td>
                            </tr>
                        </tbody>
                    </table>
                </td>
            </tr>
            <tr>
                <td><br></td>
            </tr>
            %endif
            <tr>
                <td height="100%">
                    <table width="100%">
                        <tbody>
                            <tr>
                                <td width="40%" align="left">
                                    <table class="tabla_timbre">
                                        <tbody>
                                            <tr>
                                                <td class="timbre_td"> <img class="timbre_png" src="${dicc_impresion['ruta_timbre']}"><br>
                                                    Timbre Electrónico SII<br>
                                                    Res.&nbsp;${dicc_impresion['texto_resol']}&nbsp;-&nbsp;Verifique Documento: www.sii.cl
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </td>
                                <td align="center">
                                <!-- SI CUMPLE REQUISITOS Y ES COPIA CEDIBLE -->
                                %if dicc_impresion['cedible'] and copia == 'CEDIBLE':
                                    <table class="tabla_acuse_recibo" width="100%" height="240">
                                        <tbody>
                                            <tr>
                                                <td colspan="2" align="center"><b>Acuse derecibo</b></td>
                                            </tr>
                                            <tr>
                                                <td width="20%" >Nombre:</td>
                                                <td align="center">___________________________________</td>
                                            </tr>
                                            <tr>
                                                <td >RUT:</td>
                                                <td align="center">___________________________________</td>
                                            </tr>
                                            <tr>
                                                <td >Fecha:</td>
                                                <td align="center">___________________________________</td>
                                            </tr>
                                            <tr>
                                                <td >Recinto:</td>
                                                <td align="center">___________________________________</td>
                                            </tr>
                                            <tr>
                                                <td height="25%">Firma:</td>
                                                <td align="center">___________________________________</td>
                                            </tr>
                                            <tr>
                                                <td colspan="2" style="font-size: 8pt;">
                                                <p align="justify">El acuse de recibo que se
                                                declara en este acto, de acuerdo a lo
                                                dispuesto en la letra b) del Art. 4°, y la
                                                letra c) del Art. 5° de la Ley 19.983,
                                                acredita que la entrega de mercaderías o
                                                servicio (s) prestado (s) ha (n) sido
                                                recibido (s).</p>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                <!-- SI CUMPLE REQUISITOS Y ES COPIA CEDIBLE -->
                                %endif
                                </td>
                                <td align="right" width="25%">
                                    <table class="tabla_totales" width="100%">
                                        <tbody>
                                            <!-- Solo si es documento exento -->
                                            %if dicc_impresion['documento_exento']:
                                            <tr>
                                                <td colspan="2" style="border-bottom: 1px solid black;" align="center"><b>Totales</b></td>
                                            </tr>
                                            %endif
                                            <!-- Solo si es documento exento -->
                                            %if dicc_impresion['descuento']:
                                            <tr>
                                                <td width="45%" align="right">Descuento $</td>
                                                <td align="right">${dicc_impresion['descuento']}</td>
                                            </tr>
                                            %endif
                                            %if not dicc_impresion['documento_exento']:
                                            <tr>
                                                <td align="right">Monto Neto $</td>
                                                <td align="right">${dicc_impresion['monto_neto']}</td>
                                            </tr>
                                            %endif
                                            <tr>
                                                <td align="right">Monto Exento $</td>
                                                <td align="right">${dicc_impresion['monto_exento']}</td>
                                            </tr>
                                            %if not dicc_impresion['documento_exento']:
                                            <tr>
                                                <td align="right">${dicc_impresion['nombre_iva']} $</td>
                                                <td align="right">${dicc_impresion['monto_iva']}</td>
                                            </tr>
                                            %endif
                                            <tr>
                                                <td align="right"><b>Monto Total $</b></td>
                                                <td align="right">${dicc_impresion['monto_total']}</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <!-- SI CUMPLE REQUISITOS Y ES COPIA CEDIBLE -->
                                %if dicc_impresion['cedible'] and copia == 'CEDIBLE':
                                    <td colspan="3" class="cedible" align="right">${dicc_impresion['cedible']}</td>
                                %else:
                                    <td colspan="3" class="cedible" align="right"><br></td>
                                %endif
                                <!-- SI CUMPLE REQUISITOS Y ES COPIA CEDIBLE -->
                            </tr>
                        </tbody>
                    </table>
                </td>
            </tr>
        </tbody>
    </table>
    <div style="page-break-after: always;"><span style="display: none;">&nbsp;</span></div>
        %endfor
    %endfor
</body>
</html>
