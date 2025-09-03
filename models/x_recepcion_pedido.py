from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class RecepcionPedido(models.Model):
    _name = 'x.recepcion'
    _description = _('Recepción de Materia Prima')
    _order = 'id desc'

    name = fields.Char(
        string=_('Referencia'),
        required=True,
        copy=False,
        readonly=True,
        default=_('Nuevo')
    )
  
    lote_id = fields.Many2one(
        'x_lote',
        string=_('Lote'),
        domain="[('estado','=','abierto')]",
        help=_("Selecciona el lote en el que se almacenará esta recepción.")
    )
    almacen_id = fields.Many2one('x.almacen', string="Almacén")

    company_id = fields.Many2one(
        'res.company',
        string=_('Empresa'),
        default=lambda self: self.env.company,
        index=True,
        required=True
    )

    numero_camion = fields.Integer(string=_("N° Camión"), readonly=True)
    orden_id = fields.Many2one('x.orden_pedido', string=_('Orden de Pedido'), required=True)

    proveedor_id = fields.Many2one(
        'res.partner',
        string=_('Proveedor'),
        related="orden_id.proveedor_id",
        store=True,
        readonly=True
    )

    producto = fields.Char(
        string=_('Producto'),
        related="orden_id.product",
        store=True,
        readonly=True
    )

    documento_ids = fields.One2many(
        "x.recepcion.documento",
        "recepcion_id",
        string=_("Documentos Relacionados")
    )

    cantidad = fields.Float(string=_('Cantidad (MT)'), required=True, digits=(16, 4))
    precio_unitario = fields.Float(string=_('Precio Unitario'), required=True, digits=(16, 4))

    subtotal = fields.Float(string=_('Subtotal'), compute='_compute_subtotal', store=True, digits=(16, 4), readonly=True)
    merma = fields.Float(string=_('Merma (kg)'), compute='_compute_internos', store=True, digits=(16, 4), readonly=True)
    margen = fields.Float(string=_('Margen (%)'), compute='_compute_internos', store=True, digits=(16, 4), readonly=True)
    costo_total = fields.Float(string=_('Costo Total'), compute='_compute_internos', store=True, digits=(16, 4), readonly=True)
    desviacion = fields.Float(string=_('Desviación (%)'), compute='_compute_internos', store=True, digits=(16, 4), readonly=True)

    fecha_entrega = fields.Date(string=_('Fecha de Entrega'), related="orden_id.fecha_entrega", store=True, readonly=True)

    estado = fields.Selection([
        ('borrador', _('Borrador')),
        ('validada', _('Validada')),
        ('cerrada', _('Cerrada')),
        ('cancelada', _('Cancelada')),
    ], string=_("Estado"), default='borrador', tracking=True)

    camion = fields.Char(string=_('Camión / Placa'))
    sacos = fields.Integer(string=_('Cantidad de Sacos'))
    peso_neto = fields.Float(string=_('Peso Neto (kg)'))
    observaciones = fields.Text(string=_('Observaciones'))
    
    campana_id = fields.Many2one(
        "x.campana",
        related='lote_id.campana_id',
        string=_("Campaña"),
        store=True
    )

    estado_lote = fields.Selection(
        related="lote_id.estado",
        store=True,
        string=_("Estado Lote")
    )

    # -------- Validaciones de negocio --------
    def action_set_estado(self, nuevo_estado):
        for rec in self:
            rec.estado = nuevo_estado

    @api.constrains('cantidad', 'precio_unitario')
    def _check_positive_values(self):
        for rec in self:
            if rec.cantidad is not None and rec.cantidad <= 0:
                raise ValidationError(_("La cantidad debe ser mayor que 0."))
            if rec.precio_unitario is not None and rec.precio_unitario <= 0:
                raise ValidationError(_("El precio unitario debe ser mayor que 0."))

    # -------- Secuencia --------
    @api.model
    def create(self, vals):
        if not vals.get('company_id'):
            vals['company_id'] = self.env.company.id
        
        if vals.get("lote_id"):
            lote = self.env["x_lote"].browse(vals["lote_id"])
            if lote and lote.campana_id:
                vals["campana_id"] = lote.campana_id.id
        
        if not vals.get('name') or vals['name'] in (_('Nuevo'), _('New')):
            vals['name'] = self.env['ir.sequence'].with_context(
                force_company=vals['company_id']
            ).next_by_code('x.recepcion') or _('Nuevo')
        
        # --- Secuencia del número de camión por campaña ---
        if vals.get("campana_id"):
            campana = self.env["x.campana"].browse(vals["campana_id"])
            last = self.env["x.recepcion"].search([
                ("campana_id", "=", campana.id)
            ], order="numero_camion desc", limit=1)
            next_num = (last.numero_camion or 0) + 1
            vals["numero_camion"] = next_num
    
        return super().create(vals)
    
    # -------- Computes --------
    @api.depends('cantidad', 'precio_unitario')
    def _compute_subtotal(self):
        for rec in self:
            qty = rec.cantidad or 0.0
            price = rec.precio_unitario or 0.0
            rec.subtotal = round(qty * price, 4)

    @api.depends(
        'cantidad', 'precio_unitario', 'peso_neto',
        'orden_id.cantidad_mt', 'orden_id.precio_unitario',
        'orden_id.contrato_id.cantidad_total', 'orden_id.contrato_id.precio_unitario'
    )        
    def _compute_internos(self):
        for rec in self:
            cantidad_contrato = (
                rec.orden_id.cantidad_mt
                or rec.orden_id.contrato_id.cantidad_total
                or 0.0
            )
            precio_contrato = (
                rec.orden_id.precio_unitario
                or rec.orden_id.contrato_id.precio_unitario
                or 0.0
            )
             
            peso_real_kg = rec.peso_neto or 0.0
            cantidad_real_mt = rec.cantidad or 0.0
            precio_real = rec.precio_unitario or 0.0

            contrato_kg = cantidad_contrato * 1000.0
            merma = contrato_kg - peso_real_kg if contrato_kg and peso_real_kg else 0.0

            margen = 0.0
            if precio_contrato:
                margen = ((precio_real - precio_contrato) / precio_contrato) * 100.0

            costo_total = cantidad_real_mt * precio_real

            desviacion = 0.0
            if cantidad_contrato:
                desviacion = ((cantidad_real_mt - cantidad_contrato) / cantidad_contrato) * 100.0

            rec.merma = round(merma, 4)
            rec.margen = round(margen, 4)
            rec.costo_total = round(costo_total, 4)
            rec.desviacion = round(desviacion, 4)
