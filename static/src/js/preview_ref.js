/** feedbio_provision_custom/static/src/js/preview_ref.js */
odoo.define('feedbio_provision_custom.preview_ref', function (require) {
  'use strict';

  const ajax = require('web.ajax');
  const core = require('web.core');
  const _t = core._t; // función de traducción

  require('web.dom_ready'); // asegura DOM listo

  function updatePreview() {
    const selProv = document.querySelector('select[name="proveedor_id"]');
    const selCamp = document.querySelector('select[name="campana_id"]');
    const preview = document.getElementById('contract_no_preview');
    if (!preview) return;

    const proveedor_id = selProv && selProv.value;
    const campana_id   = selCamp && selCamp.value;

    const autoText = _t('Se generará automáticamente al guardar');

    if (proveedor_id && campana_id) {
      ajax.jsonRpc('/giudico/contrato/preview_ref', 'call', {
        proveedor_id: parseInt(proveedor_id),
        campana_id: parseInt(campana_id),
      }).then(function (res) {
        preview.value = (res && res.ref) ? res.ref : autoText;
        const hidden = document.querySelector('input[name="reserved_ref"]');
        if (hidden) hidden.value = (res && res.ref) ? res.ref : '';
      }).catch(function () {
        preview.value = autoText;
      });
    } else {
      preview.value = autoText;
    }
  }

  // Bind al cargar
  const prov = document.querySelector('select[name="proveedor_id"]');
  const camp = document.querySelector('select[name="campana_id"]');
  if (prov) prov.addEventListener('change', updatePreview);
  if (camp) camp.addEventListener('change', updatePreview);
  updatePreview();
});
