from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class OrdenPedido(models.Model):
    _name = 'x.orden_pedido'
    _description = _('Orden de Pedido Giudico')
    _order = 'fecha_solicitud desc'

    linea_ids = fields.One2many(
        'x.orden_pedido_linea',   # modelo hijo
        'orden_pedido_id',        # campo Many2one en el hijo
        string=_('Líneas de pedido')
    )

    name = fields.Char(
        string=_('Referencia'),
        required=True,
        copy=False,
        readonly=True,
        default=_('Nuevo')
    )
    
    company_id = fields.Many2one(
        'res.company',
        string=_('Empresa'),
        default=lambda self: self.env.company,
        index=True,
        required=True
    )

    contrato_id = fields.Many2one('x.contrato', string=_('Contrato Asociado'), required=True)
    supplier_name = fields.Char(string=_('Nombre del Proveedor'), readonly=True)
    proveedor_id = fields.Many2one('res.partner', string=_('Proveedor'), required=True)
    supplier_code = fields.Char(string=_('Internal Supplier Code'), readonly=True)
    contract_number = fields.Char(string=_('Associated Contract Number'), readonly=True)
    product = fields.Char(string=_('Product'), readonly=True)
    campaign = fields.Char(string=_('Commercialization Campaign'), readonly=True)
    campana_id = fields.Many2one('x.campana', string=_('Campaña interna'), readonly=True)
    mt_contracted = fields.Float(string=_('MT Contracted'))

    cantidad_mt = fields.Float(string=_('Cantidad (MT)'), required=True)
    lugar_entrega = fields.Char(string=_('Lugar de Entrega'), required=True)
    fecha_entrega = fields.Date(string=_('Fecha de Entrega'), required=True)
    precio_unitario = fields.Float(string=_('Precio Unitario (MT)'), required=True)
    
    fecha_solicitud = fields.Date(string=_('Fecha de Solicitud'), default=fields.Date.today)

    @api.onchange('contrato_id')
    def _onchange_contrato(self):
        if self.contrato_id:
            self.supplier_name = self.contrato_id.proveedor_id.name
            self.supplier_code = self.contrato_id.proveedor_id.ref
            self.contract_number = self.contrato_id.name
            self.product = self.contrato_id.producto.display_name
            self.campaign = self.contrato_id.campana_id.name
            self.mt_contracted = self.contrato_id.cantidad_total
            self.campana_id = self.contrato_id.campana_id 

    @api.model
    def create(self, vals):
        # Forzar compañía activa
        if not vals.get('company_id'):
            vals['company_id'] = self.env.company.id

        _logger.info("=== CREANDO ORDEN === con vals %s", vals)

        if not vals.get('name') or vals['name'] in (_('Nuevo'), _('New')):
            vals['name'] = self.env['ir.sequence'].with_context(
                force_company=vals['company_id']
            ).next_by_code('x.orden_pedido') or _('Nuevo')
            
        # ⚡ Rellenar campana_id internamente desde el contrato
        if vals.get('contrato_id'):
            contrato = self.env['x.contrato'].browse(vals['contrato_id'])
            if contrato.exists():
                vals['campana_id'] = contrato.campana_id.id if contrato.campana_id else False    
            else:
                vals['campana_id'] = False

        return super().create(vals)
