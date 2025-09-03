from odoo import http, _
import json
from odoo.http import request
from collections import defaultdict
from markupsafe import Markup

class EstadoProvisionController(http.Controller):

    @http.route('/giudico/estado_provision', type='http', auth='user', website=True)
    def estado_provision(self, **kw):
        domain_recepcion = []
        domain_contrato = []
        domain_orden = []
        domain_campana = []
        domain_proveedor = [("supplier_rank", ">", 0)]
        # --- Filtros recibidos ---
        fecha_ini        = kw.get("fecha_ini")
        fecha_fin        = kw.get("fecha_fin")
        campana_id       = kw.get("campana_id")
        proveedor_id     = kw.get("proveedor_id")
        producto         = kw.get("producto")
        estado_lote      = kw.get("estado")
        estado_contrato  = kw.get("estado_contrato")
        estado_recepcion = kw.get("estado_recepcion")

        # --- Dominios ---
        if fecha_ini:
            domain_recepcion.append(("create_date", ">=", fecha_ini))
            domain_contrato.append(("create_date", ">=", fecha_ini))
            domain_orden.append(("create_date", ">=", fecha_ini))
            
        if fecha_fin:
            domain_recepcion.append(("create_date", "<=", fecha_fin))
            domain_contrato.append(("create_date", "<=", fecha_fin))
            domain_orden.append(("create_date", "<=", fecha_fin))
            
        if campana_id:
            domain_recepcion.append(("campana_id", "=", int(campana_id)))
            domain_orden.append(("campana_id", "=", int(campana_id)))
            domain_contrato.append(("campana_id", "=", int(campana_id)))
            domain_campana.append(("id", "=", int(campana_id)))

        if proveedor_id:
            domain_recepcion.append(("proveedor_id", "=", int(proveedor_id)))
            domain_orden.append(("proveedor_id", "=", int(proveedor_id)))
            domain_contrato.append(("proveedor_id", "=", int(proveedor_id)))
            domain_proveedor.append(("id", "=", int(proveedor_id)))
            
            
        if producto:
            domain_recepcion.append(("producto", "ilike", producto))
        if estado_lote:
            domain_recepcion.append(("lote_id.estado", "=", estado_lote))
        if estado_recepcion:
            domain_recepcion.append(("estado", "=", estado_recepcion))
            
        if estado_contrato:
            domain_recepcion.append(("orden_id.contrato_id.estado", "=", estado_contrato))
            domain_orden.append(("contrato_id.estado", "=", estado_contrato))
            domain_contrato.append(("estado", "=", estado_contrato))

     
        

        vista = (kw.get("vista") or "todo").strip()
        
        if vista == "recepciones":
            recepciones = request.env["x.recepcion"].sudo().search(domain_recepcion)
            contratos = ordenes = campanas = proveedores = []
            
        elif vista == "contratos":   
            contratos = request.env["x.contrato"].sudo().search(domain_contrato)
            recepciones = ordenes = campanas = proveedores = []
            
        elif vista == "ordenes":    
            ordenes = request.env["x.orden_pedido"].sudo().search(domain_orden)
            recepciones = contratos = campanas = proveedores = []
            
            
            
            
            
        # Filtro por estado del contrato
        elif vista == "proveedores":
            proveedores = request.env["res.partner"].sudo().search(domain_proveedor)
            recepciones = contratos = ordenes = campanas = []
            
            
        elif vista == "campanas":    
            campanas = request.env["x.campana"].sudo().search(domain_campana)
            recepciones = contratos = ordenes = proveedores = []
            
        elif vista == "todo":    
            recepciones = request.env["x.recepcion"].sudo().search(domain_recepcion)
            contratos   = request.env["x.contrato"].sudo().search(domain_contrato)
            ordenes     = request.env["x.orden_pedido"].sudo().search(domain_orden)
            campanas    = request.env["x.campana"].sudo().search(domain_campana)
            proveedores = request.env["res.partner"].sudo().search(domain_proveedor)
         

        # --- Totales ---
        total_contratado = sum((r.orden_id.contrato_id.cantidad_total or 0.0) for r in recepciones)
        total_ordenado   = sum((r.orden_id.cantidad_mt or 0.0) for r in recepciones)
        total_recibido   = sum((r.cantidad or 0.0) for r in recepciones)
        total_peso       = sum((r.peso_neto or 0.0) for r in recepciones)
        total_merma      = sum((r.merma or 0.0) for r in recepciones)
        total_costo      = sum((r.costo_total or 0.0) for r in recepciones)

        n = len(recepciones)
        promedio_margen     = round((sum((r.margen or 0.0) for r in recepciones) / n), 4) if n else 0.0
        promedio_desviacion = round((sum((r.desviacion or 0.0) for r in recepciones) / n), 4) if n else 0.0

        # --- Combos ---
        
        
        

        estados_recepcion_meta = request.env["x.recepcion"].fields_get(allfields=["estado"])["estado"]["selection"]
        estados_lote_meta      = request.env["x_lote"].fields_get(allfields=["estado"])["estado"]["selection"]
        estados_contrato_meta  = request.env["x.contrato"].fields_get(allfields=["estado"])["estado"]["selection"]

        def normalize_selection(sel):
            if isinstance(sel, dict):
                return list(sel.items())
            return [(v[0], v[1]) if isinstance(v, (list, tuple)) and len(v) >= 2 else tuple(v) for v in sel]

        estados_recepcion = normalize_selection(estados_recepcion_meta)
        estados_lote      = normalize_selection(estados_lote_meta)
        estados_contrato  = normalize_selection(estados_contrato_meta)

        # --- 1) Por campaña ---
        por_campana = defaultdict(lambda: {"contratado": 0.0, "recibido": 0.0})
        for r in recepciones:
            if r.campana_id:
                por_campana[r.campana_id.name]["recibido"] += r.cantidad or 0.0
                if r.orden_id.contrato_id:
                    por_campana[r.campana_id.name]["contratado"] += r.orden_id.contrato_id.cantidad_total or 0.0

        por_campana_chart = {
            "labels": list(por_campana.keys()),
            "contratado": [round(v["contratado"], 4) for v in por_campana.values()],
            "recibido": [round(v["recibido"], 4) for v in por_campana.values()],
        }

        # --- 2) Por proveedor ---
        por_proveedor = defaultdict(lambda: {"mt": 0.0, "merma": 0.0})
        for r in recepciones:
            if r.proveedor_id:
                por_proveedor[r.proveedor_id.name]["mt"] += r.cantidad or 0.0
                por_proveedor[r.proveedor_id.name]["merma"] += r.merma or 0.0

        por_proveedor_chart = {
            "labels": list(por_proveedor.keys()),
            "mt": [round(v["mt"], 4) for v in por_proveedor.values()],
            "merma": [round(v["merma"], 4) for v in por_proveedor.values()],
        }

        # --- 3) Por mes ---
        por_mes = defaultdict(lambda: {"mt": 0.0, "monto": 0.0})
        for r in recepciones:
            if r.create_date:
                mes = r.create_date.strftime("%Y-%m")
                por_mes[mes]["mt"] += r.cantidad or 0.0
                por_mes[mes]["monto"] += r.costo_total or 0.0

        mes_labels = sorted(por_mes.keys())
        por_mes_chart = {
            "labels": mes_labels,
            "mt": [round(por_mes[m]["mt"], 4) for m in mes_labels],
            "costo": [round(por_mes[m]["monto"], 4) for m in mes_labels],
        }
        
        counters = {
          "contratos": len(contratos),
          "ordenes": len(ordenes),
          "campanas": len(campanas),
          "recepciones": len(recepciones),
          "proveedores": len(proveedores),
        }

        contratos_por_estado = defaultdict(int)
        for c in contratos:
               contratos_por_estado[c.estado] += 1
        contratos_estado_chart = {
               "labels": list(contratos_por_estado.keys()),
               "valores": list(contratos_por_estado.values())
        }   
                   
        cumplimiento_campana = { 
                                
            "labels": [],   
            "porcentajes": []
            
        }                     
        for camp, vals in por_campana.items():
            contratado = vals["contratado"]
            recibido = vals["recibido"]
            porcentaje = round((recibido / contratado * 100), 2) if contratado else 0
            cumplimiento_campana["labels"].append(camp)
            cumplimiento_campana["porcentajes"].append(porcentaje)                        
                                
                                
                                
                                
        # --- Render ---
        return request.render("feedbio_provision_custom.giudico_estado_provision_template", {
            "por_campana_chart": Markup(json.dumps(por_campana_chart)),
            "por_proveedor_chart": Markup(json.dumps(por_proveedor_chart)),
            "por_mes_chart": Markup(json.dumps(por_mes_chart)),
            "contratos_estado_chart": Markup(json.dumps(contratos_estado_chart)),
            "cumplimiento_campana": Markup(json.dumps(cumplimiento_campana)),
            "recepciones": recepciones,
            "contratos": contratos,
            "ordenes": ordenes, 
            "proveedores": proveedores,
            "campanas": campanas,
            "counters": counters,
            "vista": vista, 
            
            "estados_recepcion": estados_recepcion,
            "estados_lote": estados_lote,
            "estados_contrato": estados_contrato,
            "filtros": kw,
            "totales": {
                "contratado": total_contratado,
                "ordenado": total_ordenado,
                "recibido": total_recibido,
                "peso": total_peso,
                "merma": total_merma,
                "costo": total_costo,
                "margen": promedio_margen,
                "desviacion": promedio_desviacion,
            }
        })
