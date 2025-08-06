from odoo import models, fields

class CampanaAgricola(models.Model):
    _name = 'x.campana'
    _description = 'Campaña Agrícola'
    _order = 'anio_final desc'

    name = fields.Char(string='Nombre de la campaña', required=True)  # Ej: 2024-2025
    anio_final = fields.Char(string='Año final', required=True)  # Ej: 2025
