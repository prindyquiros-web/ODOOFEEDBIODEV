from odoo import http
from odoo.http import request
from odoo.exceptions import UserError


class CampanasController(http.Controller):

    @http.route('/giudico/mantenimiento/campanas', type='http', auth='user', website=True)
    def lista_campanas(self, **kwargs):
        Campana = request.env['x.campana'].sudo()
        campanas = Campana.search(
            [('company_id', '=', request.env.company.id)], 
            order="anio_inicial desc"
        )
        return request.render('feedbio_provision_custom.giudico_list_campanas_template', {
            'campanas': campanas
        })

    @http.route('/giudico/mantenimiento/campana/delete/<int:campana_id>', type='http', auth='user', website=True)
    def eliminar_campana(self, campana_id):
     try:   
        campana = request.env['x.campana'].sudo().browse(campana_id)
        if campana.exists() and campana.company_id == request.env.company:
            campana.unlink()
     except Exception:
         raise UserError("No se puede eliminar la campaña porque tiene contratos asociados. Archive la campaña en su lugar.")
     return request.redirect('/giudico/mantenimiento/campanas')
