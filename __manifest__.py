{
    'name': 'ODOOFEEDBIODEV',
    'version': '1.0',
    'summary': 'Gestión de provisión y recepción de soya',
    'category': 'Operations',
    'author': 'Equipo FeedBio',
    'license': 'LGPL-3',
    'depends': ['base', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'data/contrato_sequence.xml',
        'views/x_contrato_views.xml',
        'views/x_campana_views.xml',
        'views/x_proveedor_contrato_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}
