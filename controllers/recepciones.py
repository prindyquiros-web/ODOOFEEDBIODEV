from odoo import http, _
from odoo.http import request
import base64
from . import _utils_company as cu

class RecepcionPedidoController(http.Controller):

    @http.route('/giudico/recepciones', type='http', auth='user', website=True)
    def lista_recepciones(self, **kw):
        Recep = request.env['x.recepcion'].sudo()
        recepciones = Recep.search(cu.company_domain(), order="id desc")

        return request.render('feedbio_provision_custom.giudico_list_recepciones_template', {
            'recepciones': recepciones
        })

    # GET: mostrar formulario
    @http.route('/giudico/recepcion/nueva', type='http', auth='user', website=True, methods=['GET'])
    def nueva_recepcion(self, **kw):
        ordenes = cu.env_company_forced()['x.orden_pedido'].sudo().search(cu.company_domain())
        almacenes = request.env['x.almacen'].sudo().search([], order="name")

        campana = cu.env_company_forced()['x.campana'].sudo().search(
            cu.company_domain(), order="anio_final desc", limit=1
        )
        lotes = cu.env_company_forced()['x_lote'].sudo().search(
            cu.company_domain() + [('estado','=','abierto')]
        )

        next_num = 1
        if campana:
            last = request.env["x.recepcion"].sudo().search(
                [("campana_id", "=", campana.id)],
                order="numero_camion desc",
                limit=1
            )
            next_num = (last.numero_camion or 0) + 1

        return request.render('feedbio_provision_custom.giudico_nueva_recepcion_template', {
            'ordenes': ordenes,
            "numero_camion": next_num,
            "lotes": lotes,
            "campana": campana,
            "almacenes": almacenes,
        })

    # POST: crear recepción (con archivos múltiples)
    @http.route('/giudico/recepcion/nueva', type='http', auth='user', methods=['POST'], csrf=True, website=True)
    def crear_recepcion(self, **post):
        vals = {
            'orden_id': int(post.get('orden_pedido_id')),
            'cantidad': float(post.get('cantidad') or 0),
            'precio_unitario': float(post.get('precio_unitario') or 0),
            'lote_id': int(post.get('lote_id')) if post.get('lote_id') else False,
            'camion': post.get('camion'),
            'sacos': int(post.get('sacos') or 0),
            'peso_neto': float(post.get('peso_neto') or 0),
            'observaciones': post.get('observaciones'),
            "almacen_id": int(post.get("almacen_id")) if post.get("almacen_id") else False,

        }
        
        if not vals.get('company_id'):
            vals['company_id'] = request.env.company.id
        recepcion = request.env['x.recepcion'].with_context(force_company=vals['company_id']).sudo().create(vals)

        # procesar múltiples archivos
        files = request.httprequest.files.getlist('archivos[]')
        for f in files:
            if f:
                request.env['x.recepcion.documento'].sudo().create({
                    'name': f.filename,
                    'file': base64.b64encode(f.read()).decode('utf-8'),
                    'file_filename': f.filename,
                    'recepcion_id': recepcion.id,
                    'company_id': recepcion.company_id.id,
                })

        return request.redirect('/giudico/recepciones')

    # API para autocompletar datos
    @http.route('/giudico/api/orden_info/<int:orden_id>', type='json', auth='user')
    def orden_info(self, orden_id):
        orden = request.env['x.orden_pedido'].sudo().browse(orden_id)
        if not orden.exists():
            return {}
        return {
            'proveedor': orden.proveedor_id.name if orden.proveedor_id else '',
            'producto': orden.product or '',
            "cantidad_contrato": orden.cantidad_mt or 0.0,
            "precio_contrato": orden.precio_unitario or 0.0,
            'fecha_entrega': str(orden.fecha_entrega or ''),
        }

    # GET: editar recepción
    @http.route('/giudico/recepcion/editar/<int:recepcion_id>', type='http', auth='user', website=True, methods=['GET'])
    def editar_recepcion_form(self, recepcion_id, **kw):
        recepcion = cu.env_company_forced()['x.recepcion'].sudo().browse(recepcion_id)
        ordenes = cu.env_company_forced()['x.orden_pedido'].sudo().search(cu.company_domain())
        lotes = cu.env_company_forced()['x_lote'].sudo().search(
            cu.company_domain() + [('estado','=','abierto')]
        )

        return request.render('feedbio_provision_custom.giudico_editar_recepcion_template', {
            'recepcion': recepcion,
            'ordenes': ordenes,
            'numero_camion': recepcion.numero_camion, 
            'lotes': lotes,
        })

    # POST: actualizar recepción
    @http.route('/giudico/recepcion/editar/<int:recepcion_id>', type='http', auth='user', website=True, methods=['POST'])
    def editar_recepcion_save(self, recepcion_id, **post):
        recepcion = request.env['x.recepcion'].sudo().browse(recepcion_id)
        if recepcion.exists() and recepcion.company_id == request.env.company:
            recepcion.sudo().write({
                'orden_id': int(post.get('orden_pedido_id')),
                'cantidad': float(post.get('cantidad') or 0),
                'precio_unitario': float(post.get('precio_unitario') or 0),
                'lote_id': post.get('lote_id'), 
                'camion': post.get('camion'),
                'sacos': int(post.get('sacos') or 0),
                'peso_neto': float(post.get('peso_neto') or 0),
                'observaciones': post.get('observaciones'),
                "almacen_id": int(post.get("almacen_id")) if post.get("almacen_id") else False,

            })

        # procesar múltiples archivos (si suben en edición)
        files = request.httprequest.files.getlist('archivos[]')
        for f in files:
            if f:
                request.env['x.recepcion.documento'].with_context(
                    force_company=request.env.company.id
                ).sudo().create({
                    'name': f.filename,
                    'file': base64.b64encode(f.read()).decode('utf-8'),
                    'file_filename': f.filename,
                    'recepcion_id': recepcion.id,
                    'company_id': recepcion.company_id.id,
                })

        return request.redirect('/giudico/recepciones')

    # GET: eliminar recepción
    @http.route('/giudico/recepcion/eliminar/<int:recepcion_id>', type='http', auth='user', website=True)
    def eliminar_recepcion(self, recepcion_id, **kw):
        recepcion = request.env['x.recepcion'].sudo().browse(recepcion_id)
        if recepcion.exists() and recepcion.company_id == request.env.company:
            recepcion.sudo().unlink()
        return request.redirect('/giudico/recepciones')
    
    @http.route('/giudico/documento/eliminar/<int:doc_id>', type='http', auth='user', website=True)
    def eliminar_documento(self, doc_id, **kw):
        doc = request.env['x.recepcion.documento'].sudo().browse(doc_id)
        if doc.exists() and doc.company_id == request.env.company:
            recepcion_id = doc.recepcion_id.id
            doc.unlink()
            return request.redirect('/giudico/recepcion/editar/%d' % recepcion_id)
        return request.redirect('/giudico/recepciones')

    @http.route('/giudico/recepcion/estado/<int:recepcion_id>/<string:nuevo_estado>', type='http', auth='user', website=True)
    def cambiar_estado(self, recepcion_id, nuevo_estado, **kw):
        recepcion = cu.env_company_forced()['x.recepcion'].sudo().browse(recepcion_id)
        if recepcion.exists() and recepcion.company_id == request.env.company and \
           nuevo_estado in ['borrador', 'validada', 'cerrada', 'cancelada']:
            recepcion.sudo().action_set_estado(nuevo_estado)
        return request.redirect('/giudico/recepciones')
