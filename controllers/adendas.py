from odoo import http, _
from odoo.http import request
from datetime import date

class AdendaController(http.Controller):

    @http.route('/giudico/adendas', type='http', auth='user', website=True)
    def lista_adendas(self, **kwargs):
        Adenda = request.env['x.contrato_adenda'].sudo()
        adendas = Adenda.search([('company_id', '=', request.env.company.id)], order="create_date desc")

        return request.render('feedbio_provision_custom.giudico_adendas_template', {
            'adendas': adendas
        })

    @http.route('/giudico/adenda/nueva', type='http', auth='user', website=True, methods=['GET','POST'], csrf=True)
    def nueva_adenda(self, **post):
        Adenda = request.env['x.contrato_adenda'].sudo()
        Contrato = request.env['x.contrato'].sudo()

        if request.httprequest.method == 'POST':
            vals = {
                'contrato_id': int(post.get('contrato_id')),
                'fecha': post.get('fecha') or False,

               
                'seller': post.get('seller'),
                "buyer": post.get("buyer"),
                
                'descripcion': post.get('descripcion'),
                'company_id': request.env.company.id,
            }
            if post.get('id'):
                adenda = Adenda.browse(int(post.get('id')))
                adenda.write(vals)
                return request.redirect('/giudico/adendas')    
            else:
                Adenda.create(vals)
                return request.redirect('/giudico/adendas')

        contratos = Contrato.search([])
        
        default_vals = {}
        
        if post.get('id'):
            adenda = Adenda.browse(int(post.get('id')))
            if adenda.exists():
               default_vals = adenda.read()[0]   # 👈 siempre dict
               
            
               
        else:
            adenda_tmp = Adenda.new({})
            default_vals = adenda_tmp.default_get(['seller', 'buyer', 'descripcion'])
                   
               
        return request.render('feedbio_provision_custom.giudico_nueva_adenda_template', {
            'contratos': contratos,
            'default_vals': default_vals
        })

    @http.route('/giudico/adenda/eliminar', type='http', auth='user', website=True)
    def eliminar_adenda(self, id=None, **kwargs):
        if id:
            adenda = request.env['x.contrato_adenda'].sudo().browse(int(id))
            if adenda.exists():
                adenda.unlink()
        return request.redirect('/giudico/adendas')

    @http.route('/giudico/adenda/pdf', type='http', auth='user', website=True)
    def adenda_pdf(self, id=None, **kwargs):
        adenda = request.env['x.contrato_adenda'].sudo().browse(int(id))
        if not adenda.exists():
            return request.not_found()
        pdf, _ = request.env['ir.actions.report']._render_qweb_pdf(
             'feedbio_provision_custom.action_report_adenda_pdf',   # ✅ este es el xmlid correcto
              [adenda.id]
        )
        headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', 'inline; filename="Adenda-%s.pdf"' % adenda.name)


        ]
        return request.make_response(pdf, headers=headers)
    
    
    @http.route('/giudico/adenda/cambiar_estado', type='http', auth='user', website=True)
    def cambiar_estado(self, id=None, nuevo_estado=None, **kwargs):
        Adenda = request.env['x.contrato_adenda'].sudo()
        if id and nuevo_estado in ['borrador', 'confirmada']:
           adenda = Adenda.browse(int(id))
           if adenda.exists():
              adenda.estado = nuevo_estado
        return request.redirect('/giudico/adendas')

