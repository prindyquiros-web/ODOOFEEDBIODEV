from odoo import models, fields, api, _
from datetime import date

class ContratoAdenda(models.Model):
    _name = 'x.contrato_adenda'
    _description = _('Adenda de contrato')
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha desc'

    name = fields.Char(
     string=_('Referencia'),
     required=True,
     index=True,
     readonly=True,
     copy=False,
     default="Nuevo"
    )


    contrato_id = fields.Many2one(
        'x.contrato',
        string=_('Contrato'),
        required=True
    )

    fecha = fields.Date(
        string=_('Fecha de Adenda'),
        required=True
    )
    company_id = fields.Many2one(
    'res.company',
    string=_('Empresa'),
    default=lambda self: self.env.company,
    index=True,
    required=True
    )


    contrato_numero = fields.Char(string=_('Contract No.'))
    contrato_fecha_firma = fields.Date(string=_('Fecha firma contrato original'))

    # Seller (texto completo editable)
    seller = fields.Text(
        string=_('Seller'),
        translate=True,
        default=_(
        "Seller: [NOMBRE DE TU EMPRESA]\n"
        "NIF: [XXXX]\n"
        "Dirección: [DIRECCIÓN]\n"
        "Tel: [TELÉFONO]\n"
        "Legal Representative: [REPRESENTANTE]\n"
        "ID: [CÉDULA/ID]\n"
        "Email: [EMAIL]"
       ),
        help=_("Información completa del vendedor (NIF, representante, ID, teléfono, email, etc.)")
    )

    # Buyer (texto completo editable con valores por defecto del Word)
    buyer = fields.Text(
        string=_('Buyer'),
        translate=True,
        default=_(
            "Buyer: GIUDICO BIO TOGO SARL\n"
            "NIF: 1001800860\n"
            "BÈ KPOTA NON LOIN DU CARREFOUR AGIP, LOMÉ - TOGO\n"
            "TEL: +22890123011 / +22891076307\n"
            "Legal representative: NUTSUGAH Kosiwa Mawufemo\n"
            "Identified with (ID): 0351-640-9060\n"
            "Email: management@giudicobiotogo.com"
        ),
        help=_("Información completa del comprador (editable).")
    )

    # Contenido de la adenda
    descripcion = fields.Text(string=_('Contenido de la Adenda'),translate=True)

    estado = fields.Selection([
        ('borrador', _('Borrador')),
        ('confirmada', _('Confirmada')),
    ], string=_('Estado'), default='borrador', tracking=True)

    @api.model
    def create(self, vals):
        if not vals.get('company_id'):
           vals['company_id'] = self.env.company.id
        
        if not vals.get('name') or vals.get('name').strip().lower() in ['nuevo', 'new']:
            
            vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('x.contrato_adenda_seq') or 'ADENDA-'
        return super().create(vals)

    def action_confirmar(self):
        for rec in self:
            rec.estado = 'confirmada'
