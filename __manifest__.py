{
    'name': 'feedbio_provision_custom',
    'version': '1.0',
    'summary': 'Gestión de provisión y recepción de soya',
    'category': 'Operations',
    'author': 'Equipo FeedBio',
    'license': 'LGPL-3',
    'depends': ['base', 'product','web','purchase'],
    'data': [
       'views/giudico_almacenes_template.xml',
        'views/giudico_recepciones_template.xml',
        'security/ir.model.access.csv',
        'security/feedbio_rules.xml',
        "security/feedbio_rules_extend.xml",
        'data/contrato_sequence.xml',
        'data/lote_secuencia.xml',
        
       
        'views/report_recepcion_template.xml',
        
        'views/giudico_adendas_views.xml',
        'views/feedbio_dashboard_action.xml', 
        'views/feedbio_backend_menus.xml',
        "views/report_contrato_template.xml", 
         "views/report_orden_pedido_template.xml",
        'views/menu.xml',
        'views/dashboard.xml',
        'report/report.xml',
        'views/feedbio_dashboard_template.xml',
        'views/giudico_dashboard.xml',  # <--- este es el nuevo
        'views/giudico_gestion_contratos_template.xml',
        'views/giudico_gestion_ordenpedido_template.xml',
        'views/giudico_mantenimiento_template.xml',
        'views/actions_mantenimiento.xml',
        'data/proveedor_sequence.xml',
        'views/giudico_mant_campana_template.xml',
        'views/giudico_mant_proveedor_template.xml',
        'views/giudico_list_campanas_template.xml',
        'views/giudico_list_proveedores_template.xml',
        'views/giudico_lista_lotes_template.xml',
        'views/giudico_nuevo_lote_template.xml',
        'views/estado_provision_template.xml',
        'views/giudico_lang_buttons.xml',
         'report/report_adenda_pdf_template.xml'


    ],'assets': {
    'web.assets_common': [
        'feedbio_provision_custom/static/src/js/preview_ref.js',
        'feedbio_provision_custom/static/src/js/form_validation.js',
       
    ],
    'web.assets_frontend': [
        
        'feedbio_provision_custom/static/src/js/preview_ref.js',
        'feedbio_provision_custom/static/src/js/form_validation.js',
    ],
},


    'installable': True,
    'application': True,
}
