/** feedbio_provision_custom/static/src/js/form_validation.js */
odoo.define('feedbio_provision_custom.form_validation', function (require) {
  'use strict';

  const core = require('web.core');
  const _t = core._t; // función de traducción

  require('web.dom_ready'); // asegura que el DOM esté listo

  const form = document.querySelector('.form-container form');
  if (!form) return;

  form.addEventListener('submit', function (e) {
    let missingFields = [];
    let requiredSelectors = [
      {name: 'proveedor_id', label: _t('Proveedor')},
      {name: 'campana_id', label: _t('Campaña')},
      {name: 'fecha_inicio', label: _t('Fecha de inicio')},
      {name: 'fecha_fin', label: _t('Fecha de fin')},
      {name: 'producto', label: _t('Producto contratado')},
      {name: 'cantidad_total', label: _t('Cantidad total (toneladas)')},
      {name: 'precio', label: _t('Precio estimado')},
      {name: 'forma_pago', label: _t('Forma de pago')},
      {name: 'periodo_entrega', label: _t('Periodo de entrega')},
      {name: 'lugar_entrega', label: _t('Lugar de entrega')},
      {name: 'packing', label: _t('Tipo de empaque')},
      {name: 'calidad', label: _t('Calidad')},
      {name: 'documentos_requeridos', label: _t('Documentos requeridos')},
      {name: 'fecha_firma', label: _t('Fecha de firma')},
      {name: 'disputas', label: _t('Cláusula de disputas')},
      {name: 'buyer', label: _t('Buyer')},
      {name: 'seller', label: _t('Seller')},
      {name: 'origin', label: _t('Origen')}
    ];

    // Resetear estilos
    form.querySelectorAll('input, select, textarea').forEach(el => {
      el.style.border = '';
    });

    // Revisar cada campo
    requiredSelectors.forEach(field => {
      let el = form.querySelector('[name="' + field.name + '"]');
      if (el && !el.value.trim()) {
        missingFields.push(field.label);
        el.style.border = '2px solid red';
      }
    });

    if (missingFields.length > 0) {
      e.preventDefault();
      alert(
        _t("Faltan los siguientes campos obligatorios:") + "\n" +
        missingFields.join(', ')
      );
    }
  });
});
