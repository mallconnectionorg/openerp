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
    
        %for copia in ('', '', 'CEDIBLE'):
    <table width="80mm" cellspacing="0" cellpadding="0" height="100%"
      border="0" style="padding-top: 25px;">
      <tbody>
        <tr>
          <td>
            <table style="border-collapse: collapse;" border="0">
              <tbody>
                <tr>
                  <td align="center">
                    <table width="85%" style="border-collapse: collapse;"
                      align="center" border="0">
                      <tbody>
                        <tr align="center" height="90%">
                          <td  class="recuadro_sii">R.U.T.:&nbsp;${dicc_impresion['emisor_rut']}<br>
                            ${dicc_impresion['tipo_doc']}<br>
                            <br>
                            N°&nbsp;${dicc_impresion['folio']}<br>
                          </td>
                        </tr>
                        <tr>
                          <td style="color: black;" align="center">S.I.I.&nbsp;${dicc_impresion['oficina_sii']}</td>
                        </tr>
                      </tbody>
                    </table>
                  </td>
                </tr>
                <tr><td><br></td></tr>
                <tr>
                  <td style="vertical-align: top;" align="center">
                    <table style="border-collapse: collapse;"
                      width="100%" height="100%" border="0">
                      <tbody>
                        <tr>
                          <td class="emisor_1">${dicc_impresion['emisor_rs']}</td>
                        </tr>
                        <tr>
                          <td class="emisor_2"><b>GIRO:</b>&nbsp;${dicc_impresion['emisor_giro']}</td>
                        </tr>
                        <tr>
                          <td class="emisor_3"><b>CASA MATRIZ:</b>&nbsp;${dicc_impresion['emisor_cm']}</td>
                        </tr>
                        <tr>
                          <td class="emisor_3"><b>SUCURSAL:</b>&nbsp;${dicc_impresion['emisor_suc']}</td>
                        </tr>
                        <tr>
                          <td class="emisor_3"><b>CONTACTO:</b>&nbsp;${dicc_impresion['emisor_cont']}</td>
                        </tr>
                      </tbody>
                    </table>
                  </td>
                </tr>
              </tbody>
            </table>
          </td>
        </tr>
        <tr><td><br></td></tr>
        <tr>
          <td>
            <table
              class="cliente" width="100%" height="auto">
              <tbody>
                <tr>
                  <td class="emisor_1">${dicc_impresion['receptor_rs']}</td>
                </tr>
                <tr>
                  <td><b>R.U.T:</b>&nbsp;${dicc_impresion['receptor_rut']}</td>
                </tr>
                <tr>
                  <td><b>Giro:</b>&nbsp;${dicc_impresion['receptor_giro']}</td>
                </tr>
                <tr>
                  <td><b>Dirección:</b>&nbsp;${dicc_impresion['receptor_direccion']}</td>
                </tr>
                <tr>
                  <td><b>Comuna:</b>&nbsp;${dicc_impresion['receptor_comuna']}</td>
                </tr>
                <tr>
                  <td><b>Pago:</b>&nbsp;${dicc_impresion['cond_pago']}</td>
                </tr>
              </tbody>
            </table>
            <table class="cliente" style="border-collapse: collapse;"
              width="100%">
              <tbody>
                <tr>
                  <td style="font-size: 8pt;"><br>
                  </td>
                </tr>
                <tr>
                  <td align="left"><b>${dicc_impresion['fecha_texto']}</b></td>
                </tr>
              </tbody>
            </table>
          </td>
        </tr>
        <tr>
          <td><br>
          </td>
        </tr>
        <tr>
          <td>
            <table class="tabla_encabezado_detalle" width="100%">
              <tbody>
                <tr>
                  <td>ARTÍCULO</td>
                  <td ></td>
                  <td ></td>
                </tr>
                <tr>
                  <td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;PRECIO UNITARIO</td>
                  <td width="12%" align="center">CANT.</td>
                  <td width="20%" align="right">VALOR</td>
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
                  <td>${linea_detalle['nombre']}</td>
                  <td width="12%" align="center">${linea_detalle['cantidad']}</td>
                  <td width="20%" align="right">${linea_detalle['valor']}</td>
                </tr>
                <tr>
                  <td>&nbsp;($${linea_detalle['precio_unitario']} c/u)</td>
                  <td width="12%" align="center"></td>
                  <td width="20%" align="right"></td>
                </tr>
                    %if linea_detalle['descuento']:
                        <tr>
                            <td>&nbsp;** DSCO. -${linea_detalle['descuento']}</td>
                            <td width="12%" align="center"></td>
                            <td width="20%" align="right"></td>
                        </tr>
                    %endif
                %endfor
                <!-- AQUI TERMINA EL FOR PARA LAS LINEAS DEL DETALLE -->
              </tbody>
            </table>
          </td>
        </tr>
        <tr>
            <td align="right">
                <table class="tabla_totales" width="100%">
                    <tbody>
                        <!-- Solo si es documento exento -->
                        %if dicc_impresion['documento_exento']:
                        <tr>
                            <td colspan="2" style="border-bottom: 1px
                            solid black;" align="center"><b>Totales</b>
                            </td>
                        </tr>
                        %endif
                        <!-- Solo si es documento exento -->
                        %if dicc_impresion['descuento']:
                        <tr>
                            <td width="45%" align="right">Descuento</td>
                            <td align="right">${dicc_impresion['descuento']}</td>
                        </tr>
                        %endif
                        %if not dicc_impresion['documento_exento']:
                        <tr>
                            <td align="right">Total Neto</td>
                            <td align="right">${dicc_impresion['monto_neto']}</td>
                        </tr>
                        %endif
                        <tr>
                            <td align="right">Monto Exento</td>
                            <td align="right">${dicc_impresion['monto_exento']}</td>
                        </tr>
                        %if not dicc_impresion['documento_exento']:
                        <tr>
                            <td align="right">${dicc_impresion['nombre_iva']}&nbsp;$</td>
                            <td align="right">${dicc_impresion['monto_iva']}</td>
                        </tr>
                        %endif
                        <tr>
                            <td align="right"><b>Monto Total</b></td>
                            <td align="right">${dicc_impresion['monto_total']}</td>
                        </tr>
                    </tbody>
                </table>
            </td>
        </tr>
        <tr>
          <td><br>
          </td>
        </tr>
        <tr>
          <td>
            <table class="tabla_encabezado_referencias" width="100%">
              <tbody>
                <tr>
                  <td colspan="2" align="left">Referencias a otros
                    documentos</td>
                </tr>
              </tbody>
            </table>
          </td>
        </tr>
        <tr>
          <td>
            <table class="tabla_referencias" width="100%">
              <tbody>
                <!-- AQUI DEBE IR UN FOR PARA LAS LINEAS DE LAS REFERENCIAS -->
                %for linea_referencia in dicc_impresion['referencias']:
                <tr>
                  <td colspan="2"><b>Tipo documento:</b>&nbsp;${linea_referencia['tipo_documento']}</td>
                </tr>
                <tr>
                  <td><b>Folio:</b>&nbsp;${linea_referencia['folio_ref']}</td>
                  <td><b>Fecha:</b>&nbsp;${linea_referencia['fecha_ref']}</td>
                </tr>
                <tr>
                  <td colspan="2"><b>Razón referencia:</b>&nbsp;${linea_referencia['razon_ref']}</td>
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
        <tr>
          <td><br>
          </td>
        </tr>
        <tr>
          <td height="100%">
            <table width="100%">
              <tbody>
                <tr>
                  <td width="100%" align="center">
                    <!-- SI CUMPLE REQUISITOS Y ES COPIA CEDIBLE -->
                    %if dicc_impresion['cedible'] and copia == 'CEDIBLE':
                    <table class="tabla_acuse_recibo" width="100%"
                      height="auto">
                      <tbody>
                        <tr>
                          <td colspan="2" align="center"><b>Acuse de
                              recibo</b></td>
                        </tr>
                        <tr><td><br></td></tr>
                        <tr><td><br></td></tr>
                        <tr>
                          <td width="20%" height="15%">Nombre:</td>
                          <td align="center">____________________________________</td>
                        </tr>
                        <tr><td><br></td></tr>
                        <tr>
                          <td height="15%">RUT:</td>
                          <td align="center">____________________________________</td>
                        </tr>
                        <tr><td><br></td></tr>
                        <tr>
                          <td height="15%">Fecha:</td>
                          <td align="center">____________________________________</td>
                        </tr>
                        <tr><td><br></td></tr>
                        <tr>
                          <td height="15%">Recinto:</td>
                          <td align="center">____________________________________</td>
                        </tr>
                        <tr><td><br></td></tr>
                        <tr><td><br></td></tr>
                        <tr>
                          <td height="25%">Firma:</td>
                          <td align="center">____________________________________</td>
                        </tr>
                        <tr>
                          <td colspan="2" style="font-size: 12pt;">
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
                </td>
                </tr>
                <!-- SI CUMPLE REQUISITOS Y ES COPIA CEDIBLE --> <tr>
                  <td colspan="3" class="cedible" align="right">CEDIBLE</td>
                </tr>
                %endif
                <!-- SI CUMPLE REQUISITOS Y ES COPIA CEDIBLE -->
                <tr>
                  <td width="100%" align="center">
                    <table class="tabla_timbre">
                      <tbody>
                        <tr>
                          <td class="timbre_td"> <img
                              class="timbre_png"
                              src="${dicc_impresion['ruta_timbre']}"><br>
                            Timbre Electrónico SII<br>
                            Res.&nbsp;${dicc_impresion['texto_resol']}&nbsp;-&nbsp;Verifique Documento: www.sii.cl
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </td>
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
