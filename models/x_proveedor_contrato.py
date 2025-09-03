from odoo import models, fields, api, _


class ProveedorContrato(models.Model):
    _name = 'x_proveedor_contrato'
    _description = _('Proveedor en Contrato')

    name = fields.Char(string=_("Nombre Comercial"), required=True)
    partner_id = fields.Many2one('res.partner', string=_("Proveedor (res.partner)"))
    # Mostrar el código del proveedor (ref) directamente desde res.partner
    codigo = fields.Char(
        string=_("Código"),
        related="partner_id.ref",
        store=True,
        readonly=True
    )
    company_id = fields.Many2one(
        'res.company',
        string=_("Compañía"),
        default=lambda self: self.env.company,
        index=True
    )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """
        Al seleccionar un proveedor, si no tiene código (ref), se genera automáticamente.
        """
        if self.partner_id and not self.partner_id.ref:
            self.partner_id.ref = self.env['ir.sequence'].next_by_code('res.partner.supplier.code')
        # No retornar super().create ni nada parecido en un onchange

    @api.model
    def create(self, vals):
        partner_id = vals.get('partner_id')
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            if not partner.ref:
                partner.ref = self.env['ir.sequence'].next_by_code('res.partner.supplier.code')
        # No escribir 'codigo' porque es related; se actualizará solo
        return super().create(vals)

    def write(self, vals):
        res = super().write(vals)
        # Si cambiaron el partner, asegurar que tenga ref
        if 'partner_id' in vals:
            for rec in self.filtered('partner_id'):
                if rec.partner_id and not rec.partner_id.ref:
                    rec.partner_id.ref = self.env['ir.sequence'].next_by_code('res.partner.supplier.code')
        return res


# =========================
# Extensión de res.partner: asegurar ref cuando sea proveedor
# =========================
class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _ensure_supplier_code(self):
        """
        Asignar ref a proveedores sin código (útil al crear/editar partners).
        """
        for p in self.filtered(lambda r: r.supplier_rank > 0 and not r.ref):
            p.ref = self.env['ir.sequence'].next_by_code('res.partner.supplier.code')

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        # si se crea como proveedor (supplier_rank > 0), asegurar ref
        rec._ensure_supplier_code()
        return rec

    def write(self, vals):
        res = super().write(vals)
        # si cambió el supplier_rank o limpiaron el ref, reasegurar
        if 'supplier_rank' in vals or 'ref' in vals:
            self._ensure_supplier_code()
        # Mantener sincronizados los x_proveedor_contrato que muestren el related (store=True)
        # (Realmente no hace falta write a contratos porque 'codigo' es related+store=True y recomputa)
        return res
