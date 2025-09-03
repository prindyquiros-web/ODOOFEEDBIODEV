from odoo import models, fields, api, _
from odoo.exceptions import ValidationError  

class Lote(models.Model):
    _name = 'x_lote'
    _description = _('Lote de Provisión')
    _order = 'campana_id, name'
    contrato_id = fields.Many2one(
        'x.contrato',
        string=_("Contrato"),
        required=True
    )
    name = fields.Char(string=_('Código Lote'), required=True, copy=False, readonly=True, index=True)
    recepcion_id = fields.Many2one("x.recepcion", string=_("Recepción"))
    campana_id = fields.Many2one('x.campana', string=_('Campaña'), required=True)
    proveedor_ids = fields.Many2many(
        'res.partner',
        'x_lote_res_partner_rel',
        'lote_id',
        'partner_id',
        string=_("Proveedores")
    )
    
    estado = fields.Selection([
        ('abierto', _('Abierto')),
        ('cerrado', _('Cerrado')),
        ('deshabilitado', _('Deshabilitado'))
    ], string=_('Estado'), default='abierto')
    
    company_id = fields.Many2one(
        'res.company',
        string=_('Empresa'),
        default=lambda self: self.env.company,
        index=True,
        required=True
    )

    certification_file = fields.Binary(_("Certification"))
    certification_filename = fields.Char(_("Certification Filename"))

    delivery_note_file = fields.Binary(_("Delivery Note"))
    delivery_note_filename = fields.Char(_("Delivery Note Filename"))

    packing_list_file = fields.Binary(_("Packing List"))
    packing_list_filename = fields.Char(_("Packing List Filename"))

    invoice_file = fields.Binary(_("Invoice"))
    invoice_filename = fields.Char(_("Invoice Filename"))

    capacidad_mt = fields.Float(string=_('Capacidad Total (MT)'))
    mt_actual = fields.Float(string=_('MT Acumulados'))
    observaciones = fields.Text(string=_('Observaciones'))
    almacen_id = fields.Many2one('x.almacen', string="Almacén")


    documentos_ids = fields.Many2many(
        'ir.attachment', 'lote_attachment_rel', 'lote_id', 'attachment_id',
        string=_('Documentos')
    )

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('Nuevo'):
            company_id = vals.get('company_id') or self.env.company.id
            seq = self.env['ir.sequence'].with_context(force_company=company_id).next_by_code('x_lote') or '0001'
            vals['name'] = seq

          
            if not seq:
                raise ValidationError(_("No existe secuencia con code 'x_lote'. Verifique la configuración."))
            vals['name'] = seq
        return super(Lote, self).create(vals)
