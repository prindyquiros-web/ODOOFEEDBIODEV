from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CampanaAgricola(models.Model):
    _name = 'x.campana'
    _description = _('Campaña Agrícola')
    _order = 'anio_final desc'

    name = fields.Char(
        string=_('Nombre de la campaña'),
        required=True,
        translate=True  # 👈 permite traducir el nombre de la campaña
    )
    anio_inicial = fields.Char(string=_('Año inicial'), required=True)
    anio_final = fields.Char(string=_('Año final'), required=True)
    company_id = fields.Many2one(
        'res.company',
        string=_('Empresa'),
        default=lambda self: self.env.company,
        index=True,
        required=True
    )

    @api.constrains('anio_inicial', 'anio_final')
    def _check_anios(self):
        for r in self:
            if not (
                r.anio_inicial and r.anio_final
                and len(r.anio_inicial) == 4
                and len(r.anio_final) == 4
                and r.anio_inicial.isdigit()
                and r.anio_final.isdigit()
            ):
                raise ValidationError(_("Los años deben ser numéricos de 4 dígitos."))
            if int(r.anio_inicial) >= int(r.anio_final):
                raise ValidationError(_("El año inicial debe ser menor que el año final."))

    @api.onchange('anio_inicial', 'anio_final')
    def _onchange_set_name(self):
        if (
            self.anio_inicial
            and self.anio_final
            and self.anio_inicial.isdigit()
            and self.anio_final.isdigit()
        ):
            self.name = f"{self.anio_inicial}-{self.anio_final}"
            
    @api.model
    def create(self, vals):
        if not vals.get('company_id'):
            vals['company_id'] = self.env.company.id
        return super().create(vals)
