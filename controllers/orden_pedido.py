from odoo import http, _
from odoo.http import request
from datetime import date

class OrdenPedidoController(http.Controller):

    @http.route('/giudico/orden_pedido', type='http', auth='user', website=True)
    def lista_ordenes(self, **kwargs):
        Orden = request.env['x.orden_pedido'].sudo()
        domain = []

        if kwargs.get('numero'):
            domain.append(('name', 'ilike', kwargs['numero']))
        if kwargs.get('proveedor'):
            domain.append(('supplier_name', 'ilike', kwargs['proveedor']))
        if kwargs.get('fecha_inicio'):
            domain.append(('fecha_solicitud', '>=', kwargs['fecha_inicio']))
        if kwargs.get('fecha_fin'):
            domain.append(('fecha_solicitud', '<=', kwargs['fecha_fin']))

        ordenes = Orden.search(domain + [('company_id', '=', request.env.company.id)], order="create_date desc")

        return request.render('feedbio_provision_custom.giudico_orden_pedido_template', {
            'ordenes': ordenes
        })

    @http.route('/giudico/orden_pedido/nuevo', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def nueva_orden(self, **post):
        Orden = request.env['x.orden_pedido'].sudo()
        Contrato = request.env['x.contrato'].sudo()
        contratos = Contrato.search([('estado', 'in', ['activo', 'aprobado'])], order="name")

        # Si no hay contratos disponibles, mostrar mensaje
        if not contratos:
            return request.render('feedbio_provision_custom.giudico_nueva_orden_pedido_template', {
               'mensaje': _("No hay contratos disponibles en este momento."),
               'contratos': [],
               'orden': None,
               'codigo_proveedor': '',
               'contrato_seleccionado': None,
               'datos_contrato': {}
            })

        if request.httprequest.method == 'POST':
            contrato = Contrato.browse(int(post.get('contrato_id')))
            prov_contrato = request.env['x_proveedor_contrato'].sudo().search(
                [('partner_id', '=', contrato.proveedor_id.id)], limit=1
            )
            codigo_proveedor = (prov_contrato.codigo or '').strip() if prov_contrato else ''

            vals = {
                'contrato_id': contrato.id,
                'proveedor_id': contrato.proveedor_id.id,
                'supplier_code': codigo_proveedor,
                'supplier_name': contrato.proveedor_id.name,
                'contract_number': contrato.name,
                'product': contrato.producto.display_name,
                'campaign': contrato.campana_id.name,
                'mt_contracted': float(post.get('mt_contracted') or 0),
                'cantidad_mt': float(post.get('cantidad_mt') or 0),
                'lugar_entrega': post.get('lugar_entrega'),
                'fecha_entrega': post.get('fecha_entrega'),
                'precio_unitario': float(post.get('precio_unitario') or 0),
                'company_id': request.env.company.id,
            }

            if post.get('id'):
                orden = Orden.browse(int(post.get('id')))
                orden.write(vals)
                orden.linea_ids.unlink()
            else:
                orden = Orden.create(vals)

            return request.redirect('/giudico/orden_pedido')

        # GET - carga inicial
        orden = None
        contrato_seleccionado = None
        if post.get('id'):
            orden = Orden.browse(int(post.get('id')))
            contrato_seleccionado = orden.contrato_id
        else:
            contrato_seleccionado = contratos[0]

        prov_contrato = request.env['x_proveedor_contrato'].sudo().search(
            [('partner_id', '=', contrato_seleccionado.proveedor_id.id)], limit=1
        )
        codigo_proveedor = (prov_contrato.codigo or '').strip() if prov_contrato else ''
        
        datos_contrato = {
                'supplier_name': contrato_seleccionado.proveedor_id.name or '',
                'supplier_code': codigo_proveedor,
                'contract_number': contrato_seleccionado.name or '',
                'product': contrato_seleccionado.producto.display_name or '',
                'campaign': contrato_seleccionado.campana_id.name or '',
                'mt_contracted': contrato_seleccionado.cantidad_total or 0
            }
        
        return request.render('feedbio_provision_custom.giudico_nueva_orden_pedido_template', {
            'contratos': contratos,
            'orden': orden,
            'codigo_proveedor': codigo_proveedor,
            'contrato_seleccionado': contrato_seleccionado,
            'datos_contrato': datos_contrato
        })

    @http.route('/giudico/orden_pedido/eliminar', type='http', auth='user', website=True)
    def eliminar_orden(self, id=None, **kwargs):
        if id:
            orden = request.env['x.orden_pedido'].sudo().browse(int(id))
            if orden.exists():
                orden.unlink()
        return request.redirect('/giudico/orden_pedido')

    @http.route('/giudico/orden_pedido/pdf', type='http', auth='user', website=True)
    def orden_pdf(self, id=None, **kwargs):
        orden = request.env['x.orden_pedido'].sudo().browse(int(id))
        if not orden.exists():
            return request.not_found()
        fecha_actual_str = date.today().strftime('%d/%m/%Y')
        orden = orden.with_context(fecha_actual_str=fecha_actual_str)
        pdf, _ = request.env['ir.actions.report']._render_qweb_pdf(
            'feedbio_provision_custom.report_orden_pedido_pdf_action',
            [orden.id]
        )
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', 'inline; filename="%s-%s.pdf"' % (("Orden"), orden.name))
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route('/giudico/api/contrato/<int:contrato_id>', type='json', auth='user')
    def api_get_contrato(self, contrato_id):
        contrato = request.env['x.contrato'].sudo().browse(contrato_id)
        if not contrato.exists():
            return {}

        prov_contrato = request.env['x_proveedor_contrato'].sudo().search(
            [('partner_id', '=', contrato.proveedor_id.id)], limit=1
        )
        codigo_proveedor = (prov_contrato.codigo or '').strip() if prov_contrato else ''

        return  {
            'supplier_name': contrato.proveedor_id.name or '',
            'supplier_code': codigo_proveedor,
            'contract_number': contrato.name or '',
            'product': contrato.producto.display_name or '',
            'campaign': contrato.campana_id.name or '',
            'mt_contracted': contrato.cantidad_total or 0
        }
