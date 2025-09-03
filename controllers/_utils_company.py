from odoo.http import request

def company_domain():
    """Dominio que asegura la empresa actual y sus hijas."""
    cid = request.env.company.id
    return ['|', ('company_id', '=', cid), ('company_id', 'child_of', cid)]

def env_company_forced():
    """Devuelve simplemente el env actual (no intenta with_context)."""
    return request.env
