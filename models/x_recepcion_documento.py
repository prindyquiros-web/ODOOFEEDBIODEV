from odoo import models, fields, api, _

class RecepcionDocumento(models.Model):
    _name = 'x.recepcion.documento'
    _description = _('Documentos de Recepción')
    _order = 'id desc'

    name = fields.Char(_("Nombre archivo"), required=True)
    file = fields.Binary(_("Archivo"), required=True, attachment=True)
    file_filename = fields.Char(_("Nombre archivo original"))

    recepcion_id = fields.Many2one(
        "x.recepcion",
        string=_("Recepción"),
        ondelete="cascade",
        required=True
    )

    company_id = fields.Many2one(
        "res.company",
        string=_("Empresa"),
        default=lambda self: self.env.company,
        index=True,
        required=True
    )

    @api.model
    def create(self, vals):
        if not vals.get("company_id") and vals.get("recepcion_id"):
            recepcion = self.env["x.recepcion"].browse(vals["recepcion_id"])
            if recepcion and recepcion.company_id:
                vals["company_id"] = recepcion.company_id.id
        if not vals.get("company_id"):
            vals["company_id"] = self.env.company.id        
            
        return super().create(vals)
