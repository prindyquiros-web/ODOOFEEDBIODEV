<
class ContratoProvision(models.Model):
    _name = 'x.contrato'
    _description = 'Contrato de provisión de soya'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_inicio desc'

    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company
    )

    name = fields.Char(
        string='Referencia',
        required=True,
        copy=False,
        readonly=True,
        defau<<<<<< HEAD
from odoo import models, fields, api
lt='Nuevo'
    )

    proveedor_id = fields.Many2one(
        'res.partner',
        string='Proveedor',
        required=True
    )

    codigo_proveedor = fields.Char(
        string='Código proveedor',
        compute='_compute_codigo_proveedor',
        store=True,
        readonly=True
    )

    campana_id = fields.Many2one('x.campana', string='Campaña', required=True)
    anio_campana = fields.Char(string='Año campaña', store=True, readonly=False)

    fecha_inicio = fields.Date(string='Fecha de inicio', required=True)
    fecha_fin = fields.Date(string='Fecha de fin', required=True)
    producto = fields.Many2one('product.product', string='Producto contratado', required=True)
    cantidad_total = fields.Float(string='Cantidad total (toneladas)', required=True)
    precio = fields.Float(string='Precio estimado')
    observaciones = fields.Text(string='Observaciones')
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('aprobado', 'Aprobado'),
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('finalizado', 'Finalizado'),
    ], string='Estado', default='borrador', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('proveedor_id'):
            proveedor = self.env['res.partner'].browse(vals['proveedor_id'])
            vals['codigo_proveedor'] = proveedor.ref or 'Sin datos'
        else:
            vals['codigo_proveedor'] = 'Sin datos'

        if vals.get('campana_id'):
            campana = self.env['x.campana'].browse(vals['campana_id'])
            vals['anio_campana'] = campana.anio_final or 'Sin datos'
        else:
            vals['anio_campana'] = 'Sin datos'

        if vals.get('name') == 'Nuevo':
            codigo_proveedor = vals.get('codigo_proveedor', 'XX')
            anio = vals.get('anio_campana', '0000')
            secuencia = self.env['ir.sequence'].next_by_code('x.contrato.seq') or '0001'
            vals['name'] = f"GBT-PA-{anio}-{codigo_proveedor}-{secuencia}"

        return super().create(vals)

    @api.onchange('campana_id')
    def _onchange_campana(self):
        if self.campana_id:
            self.anio_campana = self.campana_id.anio_final or 'Sin datos'
        else:
            self.anio_campana = 'Sin datos'

    @api.depends('proveedor_id')
    def _compute_codigo_proveedor(self):
        for record in self:
            record.codigo_proveedor = record.proveedor_id.ref or 'Sin datos'

    @api.onchange('proveedor_id')
    def _onchange_proveedor_id(self):
        if self.proveedor_id:
            self.codigo_proveedor = self.proveedor_id.ref or 'Sin datos'
        else:
            self.codigo_proveedor = 'Sin datos'

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



=======
from odoo import models, fields, api

class ContratoProvision(models.Model):
    _name = 'x.contrato'
    _description = 'Contrato de provisión de soya'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_inicio desc'

    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company
    )

    name = fields.Char(
        string='Referencia',
        required=True,
        copy=False,
        readonly=True,
        default='Nuevo'
    )

    proveedor_id = fields.Many2one(
        'res.partner',
        string='Proveedor',
        required=True
    )

    codigo_proveedor = fields.Char(
        string='Código proveedor',
        compute='_compute_codigo_proveedor',
        store=True,
        readonly=True
    )

    campana_id = fields.Many2one('x.campana', string='Campaña', required=True)
    anio_campana = fields.Char(string='Año campaña', store=True, readonly=False)

    fecha_inicio = fields.Date(string='Fecha de inicio', required=True)
    fecha_fin = fields.Date(string='Fecha de fin', required=True)
    producto = fields.Many2one('product.product', string='Producto contratado', required=True)
    cantidad_total = fields.Float(string='Cantidad total (toneladas)', required=True)
    precio = fields.Float(string='Precio estimado')
    observaciones = fields.Text(string='Observaciones')
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('aprobado', 'Aprobado'),
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('finalizado', 'Finalizado'),
    ], string='Estado', default='borrador', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('proveedor_id'):
            proveedor = self.env['res.partner'].browse(vals['proveedor_id'])
            vals['codigo_proveedor'] = proveedor.ref or 'Sin datos'
        else:
            vals['codigo_proveedor'] = 'Sin datos'

        if vals.get('campana_id'):
            campana = self.env['x.campana'].browse(vals['campana_id'])
            vals['anio_campana'] = campana.anio_final or 'Sin datos'
        else:
            vals['anio_campana'] = 'Sin datos'

        if vals.get('name') == 'Nuevo':
            codigo_proveedor = vals.get('codigo_proveedor', 'XX')
            anio = vals.get('anio_campana', '0000')
            secuencia = self.env['ir.sequence'].next_by_code('x.contrato.seq') or '0001'
            vals['name'] = f"GBT-PA-{anio}-{codigo_proveedor}-{secuencia}"

        return super().create(vals)

    @api.onchange('campana_id')
    def _onchange_campana(self):
        if self.campana_id:
            self.anio_campana = self.campana_id.anio_final or 'Sin datos'
        else:
            self.anio_campana = 'Sin datos'

    @api.depends('proveedor_id')
    def _compute_codigo_proveedor(self):
        for record in self:
            record.codigo_proveedor = record.proveedor_id.ref or 'Sin datos'

    @api.onchange('proveedor_id')
    def _onchange_proveedor_id(self):
        if self.proveedor_id:
            self.codigo_proveedor = self.proveedor_id.ref or 'Sin datos'
        else:
            self.codigo_proveedor = 'Sin datos'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        # Si supplier_rank no existe, no lo usamos en el dominio
        partner_fields = self.env['res.partner']._fields
        if 'supplier_rank' in partner_fields:
            domain = [('supplier_rank', '>', 0)]
        else:
            domain = []  # sin filtro por tipo de proveedor

        if self.company_id:
            domain = domain + [
                '|',
                ('company_id', '=', False),
                ('company_id', '=', self.company_id.id)
            ]
        return {'domain': {'proveedor_id': domain}}
>>>>>>> 2bb945d (Actualización módulo: cambios en vistas, modelos y menús)
