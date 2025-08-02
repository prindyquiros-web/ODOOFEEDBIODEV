from odoo import models, fields

class XContrato(models.Model):
    _name = 'x.contrato'
    _description = 'Contrato de Provisión'

    name = fields.Char(string='Referencia', required=True)
    proveedor_id = fields.Many2one('res.partner', string='Proveedor')
    fecha_inicio = fields.Date(string='Fecha de inicio')
    fecha_fin = fields.Date(string='Fecha de fin')
    producto = fields.Char(string='Producto')  # O podría ser Many2one a un producto
    observaciones = fields.Text(string='Observaciones')

