from odoo import models,_

class ReportOrdenPedido(models.AbstractModel):
    _name = 'report.feedbio_provision_custom.orden_pedido_pdf_template'
    _description = 'Reporte Orden de Pedido'

    def _get_report_values(self, docids, data=None):
        docs = self.env['x.orden_pedido'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'x.orden_pedido',
            'docs': docs,
        }
