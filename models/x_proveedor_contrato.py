from odoo import models, fields

class ProveedorContrato(models.Model):
    _name = 'x.proveedor.contrato'
    _description = 'Proveedor de Contrato'
    _order = 'codigo'

    name = fields.Char(string='Nombre del proveedor', required=True)
    codigo = fields.Char(string='Código', required=True)  # Ej: 05
    partner_id = fields.Many2one('res.partner', string='Contacto vinculado')
