odoo.define('feedbio_provision_custom.autofill_orden_pedido', function (require) {
    'use strict';
    const ajax = require('web.ajax');

    $(document).ready(function () {
        $('#contrato_id').on('change', function () {
            let id = $(this).val();
            if (id) {
                ajax.jsonRpc(`/giudico/api/contrato/${id}`, 'call', {})
                    .then(function (data) {
                        if (data) {
                            $('[name="supplier_name"]').val(data.supplier_name);
                            $('[name="supplier_code"]').val(data.supplier_code);
                            $('[name="contract_number"]').val(data.contract_number);
                            $('[name="product"]').val(data.product);
                            $('[name="campaign"]').val(data.campaign);
                            $('[name="mt_contracted"]').val(data.mt_contracted);
                        }
                    });
            }
        });
    });
});
