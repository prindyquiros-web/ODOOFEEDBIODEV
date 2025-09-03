from odoo import http, fields, _
from odoo.http import request


class FeedBioDashboard(http.Controller):

    @http.route('/feedbio/dashboard', type='http', auth='user', website=True)
    def feedbio_dashboard(self, **kwargs):
        """%s""" % _("Muestra el dashboard con el diseño FoodHut adaptado a Odoo.")
        empresas = request.env['res.company'].sudo().search([])
        contratos = request.env['x.contrato'].sudo().search([('fecha_fin', '>=', fields.Date.today())])

        return request.render('feedbio_provision_custom.feedbio_dashboard_template', {
            'empresas': empresas,
            'contratos': contratos
        })

    @http.route('/giudico/dashboard', type='http', auth='user', website=True)
    def giudico_dashboard(self, **kw):
        return request.render('feedbio_provision_custom.giudico_dashboard_template', {})

    @http.route('/giudico/mantenimiento', type='http', auth='user', website=True)
    def mantenimiento(self, **kw):
        return request.render('feedbio_provision_custom.giudico_mantenimiento_template')

    # --- Campaña ---
    @http.route('/giudico/mantenimiento/campana', type='http', auth='user', website=True)
    def giu_mant_campana(self, **kw):
        return request.render('feedbio_provision_custom.giudico_mant_campana_template')

    @http.route('/giudico/mantenimiento/campana/create', type='http', auth='user', methods=['POST'], csrf=True, website=True)
    def giu_mant_campana_create(self, **post):
        vals = {
            'anio_inicial': post.get('anio_inicial'),
            'anio_final': post.get('anio_final'),
            'name': post.get('name') or f"{post.get('anio_inicial')}-{post.get('anio_final')}",
        }
        request.env['x.campana'].sudo().create(vals)
        return request.redirect('/giudico/mantenimiento')

    # --- Lista de Proveedores ---
    @http.route('/giudico/mantenimiento/proveedores', type='http', auth='user', website=True)
    def lista_proveedores(self, **kwargs):
        proveedores_contrato = request.env['x_proveedor_contrato'].sudo().search([], order="id asc")
        
        proveedores_data = [{
              'id': p.id,
              'codigo': p.codigo  or '',
              'nombre': p.name or '',
              'telefono': p.partner_id.phone if p.partner_id else '',
              'email': p.partner_id.email if p.partner_id else ''
        } for p in proveedores_contrato]

        return request.render('feedbio_provision_custom.giudico_list_proveedores_template', {
            'proveedores': proveedores_data
        })

    # --- Crear Proveedor ---
    @http.route('/giudico/mantenimiento/proveedor/create', type='http', auth='user', methods=['POST'], csrf=True, website=True)
    def giu_mant_proveedor_create(self, **post):
        # %s
        # % _("Generar código de secuencia")
        codigo = request.env['ir.sequence'].sudo().next_by_code('x_proveedor_contrato') or _('PRV-0001')
        nombre = post.get('nombre') or post.get('name')
        telefono = post.get('telefono') or post.get('phone')
        email = post.get('email') or post.get('email')
        partner = False
        if not post.get('partner_id'):
            partner = request.env['res.partner'].sudo().create({
                'name': nombre,
                'supplier_rank': 1,
                'phone': telefono,
                'email': email
            })
        else:
            partner = request.env['res.partner'].sudo().browse(int(post.get('partner_id')))
        
        request.env['x_proveedor_contrato'].sudo().create({
            'name': nombre,
            'codigo': codigo,
            'partner_id': partner.id if partner else False
        })

        return request.redirect('/giudico/mantenimiento/proveedores')

    # --- Editar proveedor ---
    @http.route('/giudico/mantenimiento/proveedor/edit/<int:proveedor_id>', type='http', auth='user', website=True)
    def giu_mant_proveedor_edit(self, proveedor_id, **kw):
        proveedor = request.env['x_proveedor_contrato'].sudo().browse(proveedor_id)
        if not proveedor.exists():
            return request.redirect('/giudico/mantenimiento/proveedores')
        return request.render('feedbio_provision_custom.giudico_mant_proveedor_template', {
            'proveedor': proveedor,
            'nuevo_codigo': proveedor.codigo
        })

    # --- Actualizar proveedor ---
    @http.route('/giudico/mantenimiento/proveedor/update/<int:proveedor_id>', type='http', auth='user', methods=['POST'], csrf=True, website=True)
    def giu_mant_proveedor_update(self, proveedor_id, **post):
        proveedor = request.env['x_proveedor_contrato'].sudo().browse(proveedor_id)
        if proveedor.exists():
            nombre = (post.get('nombre') or post.get('name') or '').strip()
            telefono = post.get('telefono') or post.get('phone') or ''
            email = post.get('email') or ''

            if proveedor.partner_id:
                proveedor.partner_id.sudo().write({
                    'name': nombre,
                    'phone': telefono,
                    'email': email
                })

            proveedor.sudo().write({
                'name': nombre
            })

        return request.redirect('/giudico/mantenimiento/proveedores')

    # --- Eliminar proveedor ---
    @http.route('/giudico/mantenimiento/proveedor/delete/<int:proveedor_id>', type='http', auth='user', website=True)
    def giu_mant_proveedor_delete(self, proveedor_id, **kw):
        proveedor = request.env['x_proveedor_contrato'].sudo().browse(proveedor_id)
        if proveedor.exists():
            # %s
            # % _("Primero eliminar el partner si no está referenciado en otros modelos")
            if proveedor.partner_id and not request.env['x.contrato'].sudo().search([('proveedor_id', '=', proveedor.partner_id.id)], limit=1):
                proveedor.partner_id.sudo().unlink()
            proveedor.sudo().unlink()
        return request.redirect('/giudico/mantenimiento/proveedores')
    
    
    @http.route('/giudico/mantenimiento/proveedor/new', type='http', auth='user', website=True)
    def giu_mant_proveedor_new(self, **kw):
        # %s
        # % _("Generar un nuevo código automático (opcional, según tu secuencia)")
        nuevo_codigo = request.env['ir.sequence'].sudo().next_by_code('x_proveedor_contrato') or ''

        return request.render('feedbio_provision_custom.giudico_mant_proveedor_template', {
            'proveedor': False,
            'nuevo_codigo': nuevo_codigo
       })

    @http.route('/giudico/mantenimiento/campana', type='http', auth='user', website=True)
    def giu_mant_campana(self, **kw):
       return request.render('feedbio_provision_custom.giudico_mant_campana_template')
