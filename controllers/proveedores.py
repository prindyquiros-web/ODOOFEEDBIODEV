from odoo import http, _
from odoo.http import request

class ProveedoresController(http.Controller):

    # Lista de proveedores
    @http.route('/giudico/mantenimiento/proveedores', type='http', auth='user', website=True)
    def lista_proveedores(self, **kwargs):
        Partner = request.env['res.partner'].sudo().with_context(active_test=False)
        usados_ids = request.env['x.contrato'].sudo().with_context(active_test=False).search([]).mapped('proveedor_id').ids
        domain = ['|', ('supplier_rank', '>', 0), ('id', 'in', usados_ids)]
        
        partners = Partner.search(domain, order="ref asc")
        proveedores = [
             {
              'id': p.id,
              'codigo': p.ref or '',
              'nombre': p.name or '',
              'telefono': p.phone or '',
              'email': p.email or '' 
             }
             for p in partners
        ]
          
        
        
        
        return request.render('feedbio_provision_custom.giudico_list_proveedores_template', {
            'proveedores': proveedores
        })

    # Formulario de creación (muestra solo vista previa del siguiente código)
    @http.route('/giudico/mantenimiento/proveedor/new', type='http', auth='user', website=True)
    def nuevo_proveedor(self):
        seq = request.env['ir.sequence'].sudo().search(
            [('code', '=', 'res.partner.supplier.code')],
            limit=1
        )
        next_code = f"PRV-{str(seq.number_next_actual).zfill(4)}" if seq else _("PRV-0001")
        return request.render('feedbio_provision_custom.giudico_mant_proveedor_template', {
            'proveedor': False,
            'nuevo_codigo': next_code
        })

    # Formulario de edición
    @http.route('/giudico/mantenimiento/proveedor/edit/<int:proveedor_id>', type='http', auth='user', website=True)
    def editar_proveedor(self, proveedor_id):
        proveedor = request.env['res.partner'].sudo().browse(proveedor_id)
        if not proveedor.exists():
            return request.redirect('/giudico/mantenimiento/proveedores')
        return request.render('feedbio_provision_custom.giudico_mant_proveedor_template', {
            'proveedor': proveedor
        })

    # Guardar cambios en edición
    @http.route('/giudico/mantenimiento/proveedor/update/<int:proveedor_id>', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def actualizar_proveedor(self, proveedor_id, **post):
        partner = request.env['res.partner'].sudo().browse(proveedor_id)
        if not partner.exists():
            return request.redirect('/giudico/mantenimiento/proveedores')

        vals = {
            'name': post.get('name') or partner.name,
            'phone': post.get('phone') or partner.phone,
            'email': post.get('email') or partner.email,
            'supplier_rank': 1
        }
        partner.write(vals)
        return request.redirect('/giudico/mantenimiento/proveedores')

    # Guardar creación (genera el código definitivo con PRV-)
    @http.route('/giudico/mantenimiento/proveedor/create', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def crear_proveedor(self, **post):
        seq = request.env['ir.sequence'].sudo().search(
            [('code', '=', 'res.partner.supplier.code')],
            limit=1
        )
        ref_code = False
        if seq:
            ref_code = seq.with_context(force_company=request.env.company.id).next_by_id()
        else:
            ref_code = "PRV-0001"
            
        if not ref_code.startswith("PRV-"):    

            ref_code = f"PRV-{str(ref_code).zfill(4)}"


        vals = {
            'ref': ref_code,
            'name': post.get('name'),
            'phone': post.get('phone') or '',
            'email': post.get('email') or '',
            'supplier_rank': 1,
            'company_id': request.env.company.id
        }
        request.env['res.partner'].sudo().create(vals)
        return request.redirect('/giudico/mantenimiento/proveedores')
