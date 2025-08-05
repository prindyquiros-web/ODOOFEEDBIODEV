from odoo import models, fields, api

class ContratoProvision(models.Model):
    _name = 'x.contrato'
    _description = 'Contrato de provisión de soya'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha_inicio desc'

    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True, default='Nuevo')
    proveedor_id = fields.Many2one('x.proveedor.contrato', string='Proveedor', required=True)
    codigo_proveedor = fields.Char(string='Código proveedor', store=True, readonly=False)
    
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
        # Rellenar código proveedor y año campaña aunque no se usen como related
        if vals.get('proveedor_id'):
            proveedor = self.env['x.proveedor.contrato'].browse(vals['proveedor_id'])
            vals['codigo_proveedor'] = proveedor.codigo or 'Sin datos'
        else:
            vals['codigo_proveedor'] = 'Sin datos'

        if vals.get('campana_id'):
            campana = self.env['x.campana'].browse(vals['campana_id'])
            vals['anio_campana'] = campana.anio_final or 'Sin datos'
        else:
            vals['anio_campana'] = 'Sin datos'

        # Generar referencia
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

    @api.onchange('proveedor_id')
    def _onchange_proveedor(self):
        if self.proveedor_id:
            self.codigo_proveedor = self.proveedor_id.codigo or 'Sin datos'
        else:
            self.codigo_proveedor = 'Sin datos'
