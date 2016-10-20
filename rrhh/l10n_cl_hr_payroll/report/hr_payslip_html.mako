<html>
<head>



</head>


<body>
%for obj in objects:


<center><h1>Liquidacion de remuneraciones</h1></center>
<center><small>Importadora Jiménez & Sanhueza Y Cia Ltda, rut: 76.795.070-5, Casa Matriz: Ohiggins #241 Of.821 Concepción,Chile</small></center>

<table style="width:100%">
<tr>
	<th>Período:</th>
	<td>${obj.date_from} - ${obj.date_to}</td>
	<th>Sucursal:</th>
	<td>${obj.contract_id.company_id.name and obj.contract_id.company_id or ''}</td>
<tr>
<tr>
	<th>Nombre:</th>
	<td>${obj.employee_id.name}</td>
	<th>Rut:</th>
	<td>${obj.employee_id.address_home_id.vat or ''}</td>
<tr>
<tr>
	<th>Cargo:</th>
	<td>${obj.contract_id.job_id.name}</td>
	<th>Días trabajados:</th>
	<td>${ ' dias, '.join(map(lambda x: str(x.number_of_days), obj.worked_days_line_ids)) }</td>
<tr>
<tr>
	<th>Referencia:</th>
	<td>${obj.number or ''}</td>
	<th>Cuenta bancaria:</th>
	<td>${obj.employee_id.bank_account_id.acc_number and obj.employee_id.bank_account_id or ''}</td>
<tr>
</table>

<br />
<br />

<table style="width:100%">
<tr>
<th style="text-align: left;">Item</th>
<th></th>
<th style="text-align: left;">Porcentaje</th>
<th style="text-align: left;">Total</th>
</tr>
	%for line in obj.line_ids:
	<tr>
	<td>${line.name}</td>
	<td></td>
	<td>${line.rate if line.rate<>100 else ''}</td>
	<td>${line.amount}</td>
	</tr>
	%endfor
</table>
<p /><p /><p /><p />
<small>
Certifico que he recibido de Importadora Jimenez & Sanhueza y Cia Ltda a mi satisfaccion la cantidad de
monto en pesos
indicado en la presente liquidacion y no tengo cargo ni cobro alguno que hacer por ninguno de los
conceptos correspondidos en ella.
</small>
<p /><p />
<table style="width:100%">
<tr>
<td>
<p /><p /><p /><p />
_______________________________________


</td>
<td>

<p /><p /><p /><p />
________________________________________

</td>
</tr>
</table>


%endfor

 </body>

 </html>
