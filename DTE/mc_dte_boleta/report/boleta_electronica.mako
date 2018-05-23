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
    setLang(pos.partner_id.lang)
    dicc_impresion = dicc_imp(pos) 
    %>
    
        %for copia in ('1'):
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
                          <td class="emisor_2">${dicc_impresion['emisor_giro']}</td>
                        </tr>
                        <tr>
                          <td class="emisor_3">Casa Matriz:&nbsp;${dicc_impresion['emisor_cm']}</td>
                        </tr>
                        <tr>
                          <td class="emisor_3">Sucursal:&nbsp;${dicc_impresion['emisor_suc']}</td>
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
            <!-- if cliente es distinto a 66.666.666-6-->
            %if dicc_impresion['receptor_rut'] != '66.666.666-6':
            <table
              class="cliente" width="100%" height="auto">
              <tbody>
                <tr>
                  <td>${dicc_impresion['receptor_rs']}</td>
                </tr>
                <tr>
                  <td>${dicc_impresion['receptor_rut']}</td>
                </tr>
              </tbody>
            </table>
            %endif
            <!-- fin de if cliente es distinto a 66.666.666-6-->
            <table class="cliente" style="border-collapse: collapse;"
              width="100%">
              <tbody>
                <tr>
                  <td style="font-size: 8pt;"><br>
                  </td>
                </tr>
                <tr>
                  <td><b>Referencia:</b>&nbsp;${dicc_impresion['ref_pos']}</td>
                </tr>
                <tr>
                  <td><b>Emisión:</b>&nbsp;${dicc_impresion['fecha_texto']}</td>
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
                        <tr>
                            <td align="right"><b>Total:</b></td>
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
          <td height="100%">
            <table width="100%">
              <tbody>
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
                <tr>
                    <td><br></td>
                </tr>
                <tr>
                  <td width="100%" align="center">
                    <table class="tabla_acuse_recibo" width="100%"
                      height="auto">
                      <tbody>
                        <tr>
                          <td colspan="2" style="font-size: 12pt;">
                            <p align="justify">${dicc_impresion['notas']}</p>
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
