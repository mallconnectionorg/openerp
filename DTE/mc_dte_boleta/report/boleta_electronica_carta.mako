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

    %for pos in objects:
    <% 
    setLang(inv.partner_id.lang)
    dicc_impresion = dicc_imp(pos) 
    %>
    
        %for copia in ('1'):

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
                    %if dicc_impresion['receptor_rut'] != '66.666.666-6':
                    <table style="border: 1px solid rgb(0, 0, 0) !important;" class="cliente" width="100%">
                        <tbody>
                            <tr>
                                <td align="left"><b>Cliente:</b>&nbsp;${dicc_impresion['receptor_rs']}</td>
                                <td width="30%"><b>R.U.T:</b>&nbsp;${dicc_impresion['receptor_rut']}</td>
                            </tr>
                        </tbody>
                    </table>
                    %endif
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
                                
                                </td>
                                <td align="right" width="25%">
                                    <table class="tabla_totales" width="100%">
                                        <tbody>
                                            <tr>
                                                <td align="right"><b>Total $</b></td>
                                                <td align="right">${dicc_impresion['monto_total']}</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td colspan="3" class="cedible" align="right"><br></td>
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
