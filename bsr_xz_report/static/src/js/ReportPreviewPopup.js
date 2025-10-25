odoo.define('bsr_xz_report.ReportPreviewPopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _t } = require('web.core');

    class ReportPreviewPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
        }

        async printReport() {
            // This method will trigger the original PDF download logic
            this.trigger('print-report', { is_z_report: this.props.data.is_z_report });
            this.cancel(); // Close the popup after clicking print
        }

        getFormattedDate(date) {
            // Helper to format date nicely in the popup
            return moment(date).format('YYYY-MM-DD HH:mm:ss');
        }

        formatCurrency(amount) {
            return this.env.pos.format_currency(amount);
        }
    }
    ReportPreviewPopup.template = 'ReportPreviewPopup';
    ReportPreviewPopup.defaultProps = {
        confirmText: _t('Print'),
        cancelText: _t('Close'),
        title: _t('Report Preview'),
        body: '',
    };

    Registries.Component.add(ReportPreviewPopup);

    return ReportPreviewPopup;
});
