from odoo import http
from odoo.http import request
from datetime import date
from odoo import _
from . import _utils_company as cu


class FeedbioDashboardController(http.Controller):

    @http.route('/feedbio/dashboard', type='http', auth='user', website=True)
    def feedbio_dashboard(self, **kwargs):
        user = request.env.user
        # Buscar la compañía principal del usuario
        root_company = request.env['res.company'].browse(28)  # ID de FeedBio


# Obtener todas las compañías hijas de la compañía principal
        hijas = request.env['res.company'].search([
             ('parent_id', '=', root_company.id)
        ])

    # Filtrar solo las que el usuario tiene en "Allowed Companies"
        empresas = hijas & user.company_ids
        
        return request.render('feedbio_provision_custom.feedbio_dashboard_template', {
            'companies': empresas
        })

    @http.route('/feedbio/select_company/<int:company_id>', type='http',
                auth='user', website=True, csrf=True, methods=['POST'])
    def select_company(self, company_id, **kwargs):
        request.env.user.sudo().write({'company_id': company_id})
        company = request.env['res.company'].browse(company_id)
        if company.name == 'Giudico Bio Togo Sarl':
            return request.redirect('/giudico/menu')
        return request.redirect('/web')

    @http.route('/giudico/menu', type='http', auth='user', website=True)
    def giudico_menu(self, **kwargs):
        return request.render(
            'feedbio_provision_custom.giudico_main_menu_template', {})

    @http.route('/giudico/gestion_contratos',
                type='http', auth='user', website=True)
    def giudico_gestion_contratos(self, **kwargs):
        return request.render(
            'feedbio_provision_custom.giudico_gestion_contratos_template', {})



    @http.route('/giudico/contrato/nuevo', type='http', auth='user',
                website=True, methods=['GET', 'POST'], csrf=True)
    def giudico_nuevo_contrato(self, **post):
        Contrato = request.env['x.contrato'].sudo()
        
        categoria_giudico = request.env['product.category'].sudo().search([('name', '=', 'Productos Giudico')], limit=1)

       
        # === POST ===
        if request.httprequest.method == 'POST':
            try:
                # Validación detallada de campos obligatorios
                required_fields = {
                    'proveedor_id': "Proveedor",
                   
                    'campana_id': "Campaña",
                    'fecha_inicio': "Fecha de inicio",
                    'fecha_fin': "Fecha de fin",
                    'producto': "Producto contratado",
                    'cantidad_total': "Cantidad total (toneladas)",
                    'precio': "Precio estimado",
                    'observaciones': "Observaciones",
                    'forma_pago': "Forma de pago",
                     'periodo_entrega': "Periodo de entrega",
                     'lugar_entrega': "Lugar de entrega",
                     'packing': "Tipo de empaque",
                     'calidad': "Calidad",
                     'documentos_requeridos': "Documentos requeridos",
                     'fecha_firma': "Fecha de firma",
                      'disputas': "Cláusula de disputas",
                       'buyer': "Buyer",
                     'seller': "Seller",
                     'origin': "Origen",
                     'final_provision': "Final provision",
                }
                missing = [
                    label for field,
                    label in required_fields.items() if not post.get(field)]
                if missing:
                    error_msg = _("Faltan los siguientes campos obligatorios: %s") % ", ".join(missing)

                    domain_prov = [
                        ('supplier_rank', '>', 0),
                        '|', ('company_id', '=', False), ('company_id',
                                                          '=', request.env.company.id),
                    ]
                    proveedores = request.env['x_proveedor_contrato'].sudo().search([
                        ('company_id', '=', request.env.company.id)   # 👈 aquí
                    ], order='name')

                    campanas = request.env['x.campana'].sudo().search([
                       ('company_id', '=', request.env.company.id)   # 👈 aquí
                    ], order='name')

                    productos = request.env['product.product'].sudo().search([
                           ('categ_id', '=', categoria_giudico.id),
                           ('company_id', '=', request.env.company.id)   # 👈 aquí
                    ], order='display_name')


                    return request.render('feedbio_provision_custom.giudico_nuevo_contrato_template', {
                        'proveedores': proveedores,
                        'campanas': campanas,
                        'productos': productos,
                        'default_vals': post,
                        'error_msg': error_msg
                    })

                vals = {
                    'company_id': request.env.company.id,
                    'x_codigo_historico': post.get('x_codigo_historico') or False,
                    'proveedor_id': int(post.get('proveedor_id')),
                    'campana_id': int(post.get('campana_id')),
                    'fecha_inicio': post.get('fecha_inicio'),
                    'fecha_fin': post.get('fecha_fin'),
                    'producto': int(post.get('producto')),
                    'cantidad_total': float(post.get('cantidad_total') or 0),
                    'precio': post.get('precio') or False,
                    'observaciones': post.get('observaciones') or False,
                    'forma_pago': post.get('forma_pago') or False,
                    'periodo_entrega': post.get('periodo_entrega') or False,
                    'lugar_entrega': post.get('lugar_entrega') or False,
                    'packing': post.get('packing') or False,
                    'calidad': post.get('calidad') or False,
                    'documentos_requeridos': post.get('documentos_requeridos') or False,
                    'fecha_firma': post.get('fecha_firma') or False,
                    'disputas': post.get('disputas') or False,
                    'buyer': post.get('buyer') or False,
                    'seller': post.get('seller') or False,
                    'origin': post.get('origin') or False,
                    'final_provision': post.get('final_provision') or False,
                    'estado': 'borrador'

                }

                if post.get('id'):
                    contrato = Contrato.browse(int(post.get('id')))
                    contrato.write(vals)
                else:
                    contrato = Contrato.create(vals)

                # Referencia automática
                if not contrato.name or contrato.name == 'Nuevo':
                    
                    camp = request.env['x.campana'].sudo().browse(
                        int(post.get('campana_id')))
                    
                    partner_id = int(post.get('proveedor_id'))
                    prov_contrato = request.env['x_proveedor_contrato'].sudo().search([('partner_id', '=', partner_id)], limit=1)
                    codigo_proveedor = (prov_contrato.codigo or 'XX').strip() if prov_contrato else 'XX'

                    anio = (camp.anio_final or '0000')
                    campana_name = (
                        camp.name or 'default').replace(
                        ' ', '_').lower()
                    code = f"x.contrato.seq.{campana_name}"
                    seq_model = request.env['ir.sequence'].sudo()
                    seq = seq_model.search([('code', '=', code)], limit=1)
                    if not seq:
                        seq = seq_model.create({
                            'name': f"Secuencia Contrato - {campana_name}",
                            'code': code,
                            'prefix': '',
                            'padding': 4,
                            'number_next': 1,
                            'implementation': 'standard',
                            'company_id': request.env.company.id  # 👈 clave
                        })
                    numero = seq.next_by_id() or '0001'
                    ref = f"GBT-PA-{anio}-{codigo_proveedor}-{numero}"
                    contrato.sudo().write({'name': ref})

                return request.redirect(
                    '/giudico/contratos?success=1&ref=%s' % (contrato.name or ''))
            except Exception as e:
                return _("Error al guardar contrato: %s") % str(e)

        # === GET ===
        contrato_id = post.get('id') or request.params.get('id')
        contrato = None
        if contrato_id:
            contrato = Contrato.browse(int(contrato_id))

        domain_prov = [
            ('supplier_rank', '>', 0),
            '|', ('company_id', '=', False), ('company_id',
                                              '=', request.env.company.id),
        ]
        
        categoria_giudico = request.env['product.category'].sudo().search([('name', '=', 'Productos Giudico')], limit=1)

        proveedores = request.env['x_proveedor_contrato'].sudo().search([
              ('company_id', '=', request.env.company.id)
        ], order='name')

        campanas = request.env['x.campana'].sudo().search([
          ('company_id', '=', request.env.company.id)
        ], order='name')

        productos = request.env['product.product'].sudo().search([
           ('categ_id', '=', categoria_giudico.id),
           ('company_id', '=', request.env.company.id)
        ], order='display_name')

        default_vals = {
            'id': contrato.id if contrato else '',
            'name': contrato.name if contrato else _('Se generará automáticamente'),
            'proveedor_id': contrato.proveedor_id.id if contrato else '',
            'campana_id': contrato.campana_id.id if contrato else '',
            'producto': contrato.producto.id if contrato else '',
            'fecha_inicio': contrato.fecha_inicio if contrato else '',
            'fecha_fin': contrato.fecha_fin if contrato else '',
            'cantidad_total': contrato.cantidad_total if contrato else '',
            'precio': contrato.precio if contrato else _("The price is defined by both parties according to the market price at the corresponding time (delivered to Giudico Bio Togo’s warehouse in Lomé)"),
            'forma_pago': contrato.forma_pago if contrato
            else _("100% payment by cash/check, once the soybeans have been received at the Giudico Bio Togo warehouse (and the indicated documents have been received) or it is delivered in advance according to agreement between both parties."),
            'periodo_entrega': contrato.periodo_entrega if contrato else _("The parties expressly agree that any dispute arising from the interpretation or execution of this contract shall first be settled amicably. If no agreement is reached, the parties may request mediation and arbitration from one or more companies specialized in the field, based on this contract, to facilitate an amicable settlement. If disputes persist, the matter may be referred either to international arbitration administered by the International Chamber of Commerce (ICC), headquartered in London, or to the competent Togo commercial courts, at the choice of the party initiating the proceedings."),

            'lugar_entrega': contrato.lugar_entrega if contrato else _("Warehouse of GIUDICO BIO TOGO SARL, located in Baguda – Agodeke, Lomé Togo"),
            'packing': contrato.packing if contrato else _('50 kg/100 kg polypropylene bags'),
            'calidad': contrato.calidad if contrato else
            _("NON-GMO\nEuropean Union Organic Production Certification (EOS)\nUnited States Organic Production Certification (USDA-NOP)\nProtein min 41%\n Impurity max. 2.5% (If the % impurity is greater than 2.5% as a result of cleaning the organic soybeans with the machine, the seller must replenish the corresponding amount of soybeans to the buyer or pay the equivalent amount before the termination of this contract)."),
            'documentos_requeridos': contrato.documentos_requeridos if contrato else
            _("-Organic Production certification (EOS / USDA NOP)\n-Invoice\n-Packing list\n-Delivery note"),

            'fecha_firma': contrato.fecha_firma if contrato else '',

            'disputas': contrato.disputas if contrato else
            _("The parties expressly agree that any dispute arising from the interpretation or execution of this contract shall first be settled amicably.If no agreement is reached, the parties may request mediation and arbitration from one or more companies specialized in the field, based on this contract, to facilitate an amicable settlement. If disputes persist,the matter may be referred either to international arbitration administered by the International Chamber of Commerce (ICC),headquartered in London, or to the competent Togo commercial courts, at the choice of the party initiating the proceedings."),

            'observaciones': contrato.observaciones if contrato else _('Sin Observaciones'),
            'buyer': contrato.buyer if contrato else
            _("Buyer: GIUDICO BIO TOGO SARL\nNIF: 1001800860\nBÈ KPOTA NON LOIN DU CARREFOUR AGIP, LOMÉ - TOGO\nTEL: +22890123011 / +22891076307\nLegal representative:\nName: NUTSUGAH Kosiwa Mawufemo\nIdentified with (ID): 0351-640-9060\nTelephone: +228 90123011\nEmail: management@giudicobiotogo.com"),
            'seller': contrato.seller if contrato else
            _("Seller:______________________\nNIF:________________________\nLegal representative:____________________________\nName:_______________________\nIidentified with (ID):_________________\nTelephone:________________\nEmail:____________________"),
            'origin': contrato.origin if contrato else _("Togo"),

            'final_provision': contrato.final_provision if contrato else _("This Agreement and any of its provisions may not be modified, altered or added in any way, except by the signing of a document by the authorized representatives of each Party.IN WITNESS WHEREOF, the contracting parties duly represented have signed this Agreement.Done at Lomé, on xxxx, in two (2) original copies."),
           
        }

        return request.render('feedbio_provision_custom.giudico_nuevo_contrato_template', {
            'proveedores': proveedores,
            'campanas': campanas,
            'productos': productos,
            'default_vals': default_vals
        })

    @http.route('/giudico/contrato/preview_ref', type='json',
                auth='user', methods=['POST'], csrf=False)
    def giudico_preview_ref(self, proveedor_id=None, campana_id=None, **kw):
        try:
            if not (proveedor_id and campana_id):
                return {'ref': ''}

            camp = request.env['x.campana'].sudo().browse(int(campana_id))
            partner_id = int(proveedor_id)
            prov_contrato = request.env['x_proveedor_contrato'].sudo().search([('partner_id', '=', partner_id), ('company_id', '=', request.env.company.id)], limit=1)
            codigo_proveedor = (prov_contrato.codigo or 'SinDatos').strip() if prov_contrato else 'SinDatos'

            anio = (camp.anio_final or '0000')
            campana_name = (camp.name or 'default').replace(' ', '_').lower()
            code = f"x.contrato.seq.{campana_name}"
            seq = request.env['ir.sequence'].sudo().search(
                [('code', '=', code)], limit=1)
            if not seq:
                seq = request.env['ir.sequence'].sudo().create({
                    'name': f"Secuencia Contrato - {campana_name}",
                    'code': code,
                    'prefix': '',
                    'padding': 4,
                    'number_next': 1,
                    'company_id': request.env.company.id   # 👈 agrégalo
                })
            numero = str(seq.number_next).zfill(4)

            ref = f"GBT-PA-{anio}-{codigo_proveedor}-{numero}"
            return {'ref': ref}
        except Exception:
            return {'ref': ''}


    @http.route('/giudico/contrato/eliminar', type='http', auth='user', website=True)
    def giudico_contrato_eliminar(self, id=None, **kwargs):
        if id:
            contrato = request.env['x.contrato'].sudo().browse(int(id))
            if contrato.exists():
                contrato.unlink()
        return request.redirect('/giudico/contratos')

    @http.route('/giudico/contrato/pdf', type='http', auth='user', website=True)
    def giudico_contrato_pdf(self, id=None, **kwargs):
        # Aquí generarías y devolverías el PDF
        return request.not_found()  # Temporal hasta implementar

    @http.route('/giudico/contrato/estado', type='http', auth='user', website=True)
    def giudico_contrato_estado(self, id=None, **kwargs):
        contrato = request.env['x.contrato'].sudo().browse(int(id))
        return request.render(
            'feedbio_provision_custom.giudico_contrato_estado_template',
            {'contrato': contrato}
        )

    @http.route('/giudico/contrato/cambiar_estado', type='http', auth='user', website=True)
    def cambiar_estado(self, id=None, nuevo_estado=None, **kwargs):
        if id and nuevo_estado:
           contrato = request.env['x.contrato'].sudo().browse(int(id))
           if contrato.exists():
              contrato.estado = nuevo_estado
        return request.redirect('/giudico/contratos')
    
    @http.route('/giudico/contrato/pdf', type='http', auth='user', website=True)
    def giudico_contrato_pdf(self, id=None, **kwargs):
        contrato = request.env['x.contrato'].sudo().browse(int(id))
        
        if not contrato.exists():
           return request.not_found()
        report_action = request.env.ref('feedbio_provision_custom.report_contrato_pdf')
        
        fecha_actual_str  = date.today().strftime('%d/%m/%Y')
        contrato = contrato.with_context(fecha_actual_str=fecha_actual_str)
        pdf , _ = request.env['ir.actions.report']._render_qweb_pdf(
          'feedbio_provision_custom.report_contrato_pdf',
           [contrato.id]
        )
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', 'inline; filename="Contrato-%s.pdf"' % contrato.name)
        ]  
        return request.make_response(pdf, headers=pdfhttpheaders)
    
    @http.route('/giudico/contratos', type='http', auth='user', website=True)
    def lista_contratos(self, **kwargs):
        Contrato = request.env['x.contrato'].sudo()
        domain = []

    # Filtro por número de contrato
        if kwargs.get('numero'):
            domain.append(('name', 'ilike', str(kwargs['numero']).strip()))

    # Filtro por proveedor
        if kwargs.get('proveedor'):
            domain.append(('proveedor_id.name', 'ilike', str(kwargs['proveedor']).strip()))

    # Filtro por fecha de inicio
        if kwargs.get('fecha_inicio'):
             domain.append(('fecha_inicio', '>=', kwargs['fecha_inicio']))

    # Filtro por fecha de fin
        if kwargs.get('fecha_fin'):
             domain.append(('fecha_fin', '<=', kwargs['fecha_fin']))

        contratos = Contrato.search(
           domain + [('company_id', '=', request.env.company.id)],  # 👈 aquí
           order="name desc"
        )

        return request.render('feedbio_provision_custom.giudico_contratos_template', {
             'contratos': contratos,
         })  