from odoo import models, _
from datetime import date
import base64
import logging
from odoo.modules.module import get_module_resource
from babel.dates import format_date

_logger = logging.getLogger(__name__)

class ReportRecepcionPDF(models.AbstractModel):
    _name = 'report.feedbio_provision_custom.report_recepcion_pdf_template'
    _description = 'Reporte Recepción PDF'
    

    def _get_report_values(self, docids, data=None):
        user_lang = self.env.user.lang or 'es_ES'
        docs = self.env['x.recepcion'].browse(docids)

        def img_to_base64(filename):
            path = get_module_resource('feedbio_provision_custom', 'static/src/img', filename)
            if path:
                try:
                    with open(path, 'rb') as f:
                        return base64.b64encode(f.read()).decode('utf-8')
                except Exception as e:
                    _logger.error("Error leyendo imagen %s: %s", filename, e)
            return ''

        logo_giudico = img_to_base64('LogoGiudico.png')
        
        fecha_actual_str = format_date(date.today(), format='long', locale=user_lang)

        return {
            'doc_ids': docs.ids,
            'doc_model': 'x.recepcion',
            'docs': docs,
            'fecha_actual_str': fecha_actual_str,
            'logo_giudico': logo_giudico,
        }
