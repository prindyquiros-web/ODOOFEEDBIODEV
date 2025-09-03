from odoo import models, fields, _, api
from odoo.exceptions import ValidationError

class Almacen(models.Model):
    _name = 'x.almacen'
    _description = _('Lugar de almacenamiento')
    _order = 'name'

    name = fields.Char(string=_('Nombre'), required=True, index=True)
    capacidad_mt = fields.Float(string=_('Capacidad (MT)'), digits=(16, 4))
    estado = fields.Selection([
        ('abierto', _('Abierto')),
        ('cerrado', _('Cerrado')),
    ], string=_('Estado'), default='abierto', required=True)
    company_id = fields.Many2one(
        'res.company', string=_('Compañía'),
        required=True, default=lambda self: self.env.company
    )

    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)',
         'Ya existe un almacén con ese nombre en la compañía.')
    ]
