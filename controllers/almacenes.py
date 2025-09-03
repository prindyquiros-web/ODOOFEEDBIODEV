from odoo import http, _
from odoo.http import request

class AlmacenController(http.Controller):

    @http.route('/giudico/almacenes', type='http', auth='user', website=True)
    def lista_almacenes(self, **kwargs):
        almacenes = request.env['x.almacen'].sudo().search([
            ('company_id', '=', request.env.company.id)
        ], order="name")
        return request.render('feedbio_provision_custom.giudico_almacenes_template', {
            'almacenes': almacenes
        })

    @http.route('/giudico/almacen/nuevo', type='http', auth='user', website=True, methods=['GET', 'POST'], csrf=True)
    def nuevo_almacen(self, **post):
        Almacen = request.env['x.almacen'].sudo()
        if request.httprequest.method == 'POST':
            Almacen.create({
                'name': post.get('name'),
                'capacidad_mt': float(post.get('capacidad_mt') or 0),
                'estado': post.get('estado'),
                'company_id': request.env.company.id
            })
            return request.redirect('/giudico/almacenes')
        return request.render('feedbio_provision_custom.giudico_nuevo_almacen_template')

    @http.route('/giudico/almacen/editar', type='http', auth='user', website=True, methods=['GET', 'POST'], csrf=True)
    def editar_almacen(self, id=None, **post):
        almacen = request.env['x.almacen'].sudo().browse(int(id))
        if request.httprequest.method == 'POST' and almacen.exists():
            almacen.write({
                'name': post.get('name'),
                'capacidad_mt': float(post.get('capacidad_mt') or 0),
                'estado': post.get('estado')
            })
            return request.redirect('/giudico/almacenes')
        return request.render('feedbio_provision_custom.giudico_editar_almacen_template', {
            'almacen': almacen
        })

    @http.route('/giudico/almacen/eliminar', type='http', auth='user', website=True)
    def eliminar_almacen(self, id=None, **kwargs):
        almacen = request.env['x.almacen'].sudo().browse(int(id))
        if almacen.exists():
            almacen.unlink()
        return request.redirect('/giudico/almacenes')

    @http.route('/giudico/almacen/cambiar_estado', type='http', auth='user', website=True)
    def cambiar_estado(self, id=None, **kwargs):
        almacen = request.env['x.almacen'].sudo().browse(int(id))
        if almacen.exists():
            almacen.estado = 'cerrado' if almacen.estado == 'abierto' else 'abierto'
        return request.redirect('/giudico/almacenes')
