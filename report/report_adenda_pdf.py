from odoo import models, _
from datetime import date
import base64
import logging
from odoo.modules.module import get_module_resource
from babel.dates import format_date   # 👈 Import necesario para usar format_date

_logger = logging.getLogger(__name__)

class ReportAdendaPDF(models.AbstractModel):
    _name = 'report.feedbio_provision_custom.report_adenda_pdf_template'
    _description = _('Reporte Adenda PDF')

    def _get_report_values(self, docids, data=None):
        docs = self.env['x.contrato_adenda'].browse(docids)

        def img_to_base64(filename):
            # Buscar el archivo dentro del módulo usando API de Odoo
            path = get_module_resource('feedbio_provision_custom', 'static/src/img', filename)
            if path:
                try:
                    with open(path, 'rb') as f:
                        _logger.info(">>> Imagen encontrada: %s", filename)
                        return base64.b64encode(f.read()).decode('utf-8')
                except Exception as e:
                    _logger.error(">>> Error al leer la imagen %s: %s", filename, e)
            else:
                _logger.warning(">>> No se encontró la ruta de la imagen: %s", filename)
            return ''

        logo_giudico = img_to_base64('LogoGiudico.png')
        pie_pagina = img_to_base64('Piepagina.png')

        # Log para verificar que sí se cargaron
        _logger.info(">>> logo_giudico cargado: %s", bool(logo_giudico))
        _logger.info(">>> pie_pagina cargado: %s", bool(pie_pagina))

        # Formateo de fecha según idioma del usuario
        user_lang = self.env.user.lang or 'es_ES'
        fecha_actual_str = format_date(date.today(), format='long', locale=user_lang)

        return {
            'doc_ids': docs.ids,
            'doc_model': 'x.contrato_adenda',
            'docs': docs,
            'fecha_actual_str': fecha_actual_str,
            'logo_giudico': logo_giudico,
            'pie_pagina': pie_pagina,
        }
