from odoo import http
from odoo.http import request
from odoo.http import content_disposition
import base64


class LotesController(http.Controller):

    @http.route('/giudico/lotes', type='http', auth='user', website=True)
    def lista_lotes(self, **kw):
        # Ordenamos por campaña y proveedor
        lotes = request.env['x_lote'].sudo().search(
         [('company_id', '=', request.env.company.id)],
         order="campana_id, name"
        )
        return request.render('feedbio_provision_custom.giudico_lista_lotes_template', {
            'lotes': lotes
        })

    @http.route('/giudico/lotes/nuevo', type='http', auth='user', website=True, methods=['GET', 'POST'], csrf=True)
    def nuevo_lote(self, **post):
        if request.httprequest.method == 'POST':
            proveedores_seleccionados = post.get('proveedor_ids') or []
            if not isinstance(proveedores_seleccionados, list):
                proveedores_seleccionados = [proveedores_seleccionados]
            vals = {
                'campana_id': post.get('campana_id'),
                'proveedor_ids': [(6, 0, [int(pid) for pid in proveedores_seleccionados])],
                'contrato_id': int(post.get('contrato_id')) if post.get('contrato_id') else False,
                'almacen_id': int(post.get('almacen_id')) if post.get('almacen_id') else False,
                'capacidad_mt': post.get('capacidad_mt'),
                'mt_actual': post.get('mt_actual'),
                'observaciones': post.get('observaciones'),
                'estado': 'abierto',  # por defecto
                'company_id': request.env.company.id,
            }
            request.env['x_lote'].sudo().create(vals)
            return request.redirect('/giudico/lotes')

        campanas = request.env['x.campana'].sudo().search(
            [('company_id', '=', request.env.company.id)]
        )    
        proveedores = request.env['res.partner'].sudo().search(
              [('supplier_rank', '>', 0),
              '|',
               ('company_id', '=', False),
               ('company_id', '=', request.env.company.id)]
        )   
        
        almacenes = request.env['x.almacen'].sudo().search(
             [('company_id', '=', request.env.company.id)]
        )
        
        contratos = request.env['x.contrato'].sudo().search(
             [('estado', 'in', ['activo', 'aprobado']),
              ('company_id', '=', request.env.company.id)]
        )
        return request.render('feedbio_provision_custom.giudico_nuevo_lote_template', {
            'campanas': campanas,
            'proveedores': proveedores,
            'lote': False,
            'almacenes': almacenes,
             'contratos': contratos
            
        })

    # ---------- EDITAR LOTE ----------
    @http.route('/giudico/lotes/editar/<int:lote_id>', type='http', auth='user', website=True, methods=['GET', 'POST'], csrf=True)
    def editar_lote(self, lote_id, **post):
        lote = request.env['x_lote'].sudo().browse(lote_id)
        if not lote.exists():
            return request.redirect('/giudico/lotes')

        if request.httprequest.method == 'POST':
            proveedores_seleccionados = post.get('proveedor_ids') or []
            if not isinstance(proveedores_seleccionados, list):
                proveedores_seleccionados = [proveedores_seleccionados]
                
            vals={
                'proveedor_ids': [(6, 0, [int(pid) for pid in proveedores_seleccionados])],
                'contrato_id': int(post.get('contrato_id')) if post.get('contrato_id') else False,
                'almacen_id': int(post.get('almacen_id')) if post.get('almacen_id') else False,
                'capacidad_mt': post.get('capacidad_mt'),
                'mt_actual': post.get('mt_actual'),
                'observaciones': post.get('observaciones'),
            }
            
            if not lote.exists() or lote.company_id != request.env.company:
                return request.redirect('/giudico/lotes')
            
            if post.get('campana_id'):
                vals['campana_id'] = int(post.get('campana_id'))
                
            lote.sudo().write(vals)
            return request.redirect('/giudico/lotes')   
        
          

        campanas = request.env['x.campana'].sudo().search(
            [('company_id', '=', request.env.company.id)]
        )    
        proveedores = request.env['res.partner'].sudo().search(
          [('supplier_rank', '>', 0),
            '|',
           ('company_id', '=', False),
           ('company_id', '=', request.env.company.id)]
        )
        almacenes = request.env['x.almacen'].sudo().search(
             [('company_id', '=', request.env.company.id)]
        )
        contratos = request.env['x.contrato'].sudo().search(
             [('estado', 'in', ['activo', 'aprobado']),
              ('company_id', '=', request.env.company.id)]
        )
        return request.render('feedbio_provision_custom.giudico_nuevo_lote_template', {
            'campanas': campanas,
            'proveedores': proveedores,
            'lote': lote,
            'contratos': contratos,
            'almacenes': almacenes
        })

    # ---------- ELIMINAR LOTE ----------
    @http.route('/giudico/lotes/eliminar/<int:lote_id>', type='http', auth='user', website=True)
    def eliminar_lote(self, lote_id, **kw):
        lote = request.env['x_lote'].sudo().browse(lote_id)
        if lote.exists() and lote.company_id == request.env.company:
            lote.sudo().unlink()
        return request.redirect('/giudico/lotes')

    # ---------- ACCIONES DE LOTE ----------
    @http.route('/giudico/lotes/activar', type='http', auth='user', website=True)
    def activar_lote(self, **kw):
        lote_id = kw.get('id')
        lote = request.env['x_lote'].sudo().browse(int(lote_id))
        if lote.exists() and lote.company_id == request.env.company:
            lote.estado = 'abierto'
        return request.redirect('/giudico/lotes')

    @http.route('/giudico/lotes/deshabilitar', type='http', auth='user', website=True)
    def deshabilitar_lote(self, **kw):
        lote_id = kw.get('id')
        lote = request.env['x_lote'].sudo().browse(int(lote_id))
        if lote.exists() and lote.company_id == request.env.company:
            lote.estado = 'deshabilitado'
        return request.redirect('/giudico/lotes')

    @http.route('/giudico/lotes/cerrar', type='http', auth='user', website=True)
    def cerrar_lote(self, **kw):
        lote_id = kw.get('id')
        lote = request.env['x_lote'].sudo().browse(int(lote_id))
        if lote.exists() and lote.company_id == request.env.company:
            lote.estado = 'cerrado'
        return request.redirect('/giudico/lotes')

    # ---------- DOCUMENTOS DEL LOTE ----------
    @http.route('/giudico/lotes/doc/<string:tipo>', type='http', auth='user', website=True)
    def documentos_lote(self, tipo=None, **kw):
        lote_id = kw.get('id')
        lote = request.env['x_lote'].sudo().browse(int(lote_id))
        if not lote.exists() or lote.company_id != request.env.company:
            return request.not_found()
        
        file_field = f"{tipo}_file"
        name_field = f"{tipo}_filename"
        
        filecontent = getattr(lote, file_field, False)
        filename = getattr(lote, name_field, False) or f"{tipo}.dat"
        
        if not filecontent:
            return request.not_found()
        

        return request.make_response(
            base64.b64decode(filecontent),
            headers=[
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', content_disposition(filename))
            ]
        )

    # ---------- SUBIR DOCUMENTOS ----------
    @http.route('/giudico/lotes/upload/<int:lote_id>/<string:tipo>', 
                type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def upload_documento(self, lote_id, tipo, **post):
        lote = request.env['x_lote'].sudo().browse(lote_id)
        if not lote.exists() or lote.company_id != request.env.company:
            return request.redirect('/giudico/lotes')

        file = post.get('file')
        if file:
            data = file.read()
            lote.sudo().write({
                f"{tipo}_file": base64.b64encode(data),
                f"{tipo}_filename": file.filename
            })
        return request.redirect('/giudico/lotes')

    @http.route('/giudico/lotes/delete_file/<int:lote_id>/<string:tipo>', type='http', auth='user', website=True)
    def delete_file(self, lote_id, tipo, **kw):
        lote = request.env['x_lote'].sudo().browse(lote_id)
        if lote.exists() and lote.company_id == request.env.company:
            lote.sudo().write({
                f"{tipo}_file": False,
                f"{tipo}_filename": False
            })
        return request.redirect('/giudico/lotes')
