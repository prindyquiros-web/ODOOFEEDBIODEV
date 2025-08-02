{
    'name': 'Feedbio Provisión',
    'version': '1.0',
    'summary': 'Gestión de provisión y recepción de soya',
    'category': 'Operations',
    'author': 'Equipo FeedBio',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/x_contrato_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

