from odoo import models, fields, api, _

class OrdenPedidoLinea(models.Model):
    _name = 'x.orden_pedido_linea'
    _description = _('Línea de orden de pedido')

    orden_pedido_id = fields.Many2one(
        'x.orden_pedido',
        string=_('Orden de pedido'),
        required=True,
        ondelete='cascade'
    )
    producto = fields.Many2one(
        'product.product',
        string=_('Producto'),
        required=True
    )
    cantidad = fields.Float(string=_('Cantidad (MT)'), required=True)
    precio_unitario = fields.Float(string=_('Precio unitario'), required=True)
    subtotal = fields.Float(
        string=_('Subtotal'),
        compute='_compute_subtotal',
        store=True
    )

    @api.depends('cantidad', 'precio_unitario')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.cantidad * rec.precio_unitario
