from odoo import models, fields, api, _
from odoo.addons.feedbio_provision_custom.controllers import _utils_company as cu


class ContratoProvision(models.Model):
    _name = 'x.contrato'
    _description = ('Contrato de provisión de soya')
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_inicio desc'

    company_id = fields.Many2one(
        'res.company', 
        string=('Compañía'), 
        required=True, 
        default=lambda self: self.env.company
    )
    name = fields.Char(
        string=('Referencia'), 
        required=True, 
        copy=False, 
        readonly=True, 
        default=('Nuevo')
    )
    x_codigo_historico = fields.Char(string=_('Código Histórico'))

    proveedor_id = fields.Many2one('res.partner', string=('Proveedor'), required=True)
    codigo_proveedor = fields.Char(string=('Código proveedor'), compute='_compute_codigo_proveedor', store=True, readonly=True)

    campana_id = fields.Many2one('x.campana', string=('Campaña'), required=True)
    anio_campana = fields.Char(string=('Año campaña'), store=True)

    fecha_inicio = fields.Date(string=('Fecha de inicio'), required=True)
    fecha_fin = fields.Date(string=('Fecha de fin'), required=True)
    producto = fields.Many2one('product.product', string=('Producto contratado'), required=True)
    cantidad_total = fields.Float(string=('Cantidad total (toneladas)'), required=True)

    buyer = fields.Text(string=('Buyer'))
    seller = fields.Text(string=('Seller'))
    origin = fields.Char(string=('Origin'))

    precio = fields.Text(string=('Precio estimado'))
    final_provision = fields.Text(string=('Final provision'))

    observaciones = fields.Text(string=('Observaciones'))

    estado = fields.Selection([
        ('borrador', ('Borrador')),
        ('aprobado', ('Aprobado')),
        ('activo', ('Activo')),
        ('inactivo', ('Inactivo')),
        ('finalizado', ('Finalizado')),
    ], string=('Estado'), default='borrador', tracking=True)

    calidad = fields.Text(string=('Calidad del producto'))
    packing = fields.Text(string=('Tipo de empaque'))
    documentos_requeridos = fields.Text(string=('Documentos requeridos'))
    lugar_entrega = fields.Text(string=('Lugar de entrega'))
    forma_pago = fields.Text(string=('Condiciones de pago'))
    periodo_entrega = fields.Text(string=('Periodo de entrega'))
    disputas = fields.Text(string=('Cláusula de disputas'))
    fecha_firma = fields.Date(string=('Fecha de firma del contrato'))
    precio_unitario = fields.Float(string=("Precio unitario ($/ton)"), digits=(16,4))


    @api.model
    def create(self, vals):
        if not vals.get('company_id'):
           vals['company_id'] = self.env.company.id
        # ✅ Usar siempre código de x_proveedor_contrato
        if vals.get('proveedor_id'):
            partner_id = vals['proveedor_id']
            prov_contrato = self.env['x_proveedor_contrato'].sudo().search(
                [('partner_id', '=', partner_id)], limit=1
            )
            vals['codigo_proveedor'] = prov_contrato.codigo or ('Sin datos')
        else:
            vals['codigo_proveedor'] = ('Sin datos')

        if vals.get('campana_id'):
            campana = self.env['x.campana'].browse(vals['campana_id'])
            vals['anio_campana'] = campana.anio_final or ('Sin datos')
        else:
            vals['anio_campana'] = ('Sin datos')
            
        if not vals.get('name') or '????' in vals.get('name') or vals.get('name') == ('Nuevo'):
            codigo_proveedor = vals.get('codigo_proveedor', 'XX')
            anio = vals.get('anio_campana', '0000')

            campana_name = 'default'
            if vals.get('campana_id'):
                campana = self.env['x.campana'].browse(vals['campana_id'])
                if campana and campana.name:
                    campana_name = campana.name.replace(' ', '_').lower()

            codigo_campana = f"x.contrato.seq.{campana_name}"
            sequence_model = self.env['ir.sequence']
            seq = sequence_model.search([('code', '=', codigo_campana),('company_id', '=', vals['company_id'])], limit=1)

            if not seq:
                seq = sequence_model.create({
                    'name': ('Secuencia Contrato - %s') % campana_name,
                    'code': codigo_campana,
                    'prefix': '',
                    'padding': 4,
                    'number_next': 1,
                    'implementation': 'standard',
                    'company_id': vals['company_id']
                })

            secuencia = seq.with_context(force_company=vals['company_id']).next_by_id() or '0001'
            vals['name'] = f"GBT-PA-{anio}-{codigo_proveedor}-{secuencia}"

        return super().create(vals)

    @api.depends('proveedor_id')
    def _compute_codigo_proveedor(self):
        # ✅ Calcular usando x_proveedor_contrato
        for record in self:
            if record.proveedor_id:
                prov_contrato = self.env['x_proveedor_contrato'].sudo().search(
                    [('partner_id', '=', record.proveedor_id.id)], limit=1
                )
                record.codigo_proveedor = prov_contrato.codigo or ('Sin datos')
            else:
                record.codigo_proveedor = ('Sin datos')

    @api.onchange('proveedor_id')
    def _onchange_proveedor_id(self):
        # ✅ También en el onchange del backend
        if self.proveedor_id:
            prov_contrato = self.env['x_proveedor_contrato'].sudo().search(
                [('partner_id', '=', self.proveedor_id.id)], limit=1
            )
            self.codigo_proveedor = prov_contrato.codigo or ('Sin datos')
        else:
            self.codigo_proveedor = ('Sin datos')


    @api.onchange('company_id')
    def _onchange_company_id(self):
        domain = [('supplier_rank', '>', 0)]
        if self.company_id:
            domain = [
                ('supplier_rank', '>', 0),
                '|',
                ('company_id', '=', False),
                ('company_id', '=', self.company_id.id)
            ]
        return {'domain': {'proveedor_id': domain}}

    @api.onchange('proveedor_id', 'campana_id')
    def _onchange_name_preview(self):
        if self.proveedor_id and self.campana_id:
            codigo_proveedor = self.proveedor_id.ref or 'XX'
            anio = self.campana_id.anio_final or '0000'
            campana_name = self.campana_id.name.replace(' ', '_').lower() if self.campana_id.name else 'default'
            codigo_campana = f"x.contrato.seq.{campana_name}"

            sequence_model = self.env['ir.sequence']
            seq = sequence_model.search([('code', '=', codigo_campana), ('company_id', '=', self.company_id.id)], limit=1)
            if seq:
                numero = str(seq.number_next).zfill(4)
            else:
                numero = '0001'

            self.name = f"GBT-PA-{anio}-{codigo_proveedor}-{numero}"
        else:
            self.name = ('Nuevo')

    def action_aprobar(self):
        for rec in self:
            rec.estado = 'aprobado'

    def action_activar(self):
        for rec in self:
            rec.estado = 'activo'

    def action_finalizar(self):
        for rec in self:
            rec.estado = 'finalizado'

    def print_contrato_pdf(self):
        return self.env.ref('feedbio_provision_custom.report_contrato_pdf').report_action(self)
