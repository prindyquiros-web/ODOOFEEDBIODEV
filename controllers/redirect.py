from odoo import http
from odoo.http import request

class RedirectDashboard(http.Controller):

    @http.route('/', type='http', auth='user')
    def root_redirect(self, **kw):
        """
        Si un usuario entra a http://localhost:8071 → redirigir al dashboard
        """
        return request.redirect('/feedbio/dashboard')

    @http.route('/webadmin', type='http', auth='user')
    def web_admin(self, **kw):
        """
        Ruta alternativa para abrir el backend estándar de Odoo
        (sin redirecciones al dashboard).
        """
        return request.redirect('/web')
