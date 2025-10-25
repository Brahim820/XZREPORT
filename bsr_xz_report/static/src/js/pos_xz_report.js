odoo.define('bsr_xz_report.pos_xz_report', function (require) {
    "use strict";

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');
    const { _t } = require('web.core');

    class XZReportButtons extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click-x-report', this.onClickXReport);
            useListener('click-z-report', this.onClickZReport);
        }

        get xReportText() {
            return this.env._t('X Report');
        }

        get zReportText() {
            return this.env._t('Z Report');
        }

        // The old PDF generation methods, now triggered from the popup
        async _printReport(is_z_report) {
            const session_id = this.env.pos.pos_session.id;
            const method = is_z_report ? 'generate_z_report' : 'generate_x_report';
            try {
                const report_action = await rpc.query({
                    model: 'pos.session',
                    method: method,
                    args: [[session_id]],
                });
                if (report_action) {
                    this.env.pos.do_action(report_action);
                }
            } catch (error) {
                const title = is_z_report ? this.env._t('Z Report Error') : this.env._t('X Report Error');
                const body = is_z_report ? this.env._t('Could not generate the Z report.') : this.env._t('Could not generate the X report.');
                this.showPopup('ErrorPopup', { title, body });
            }
        }

        // New methods to show the preview popup
        async onClickXReport() {
            const reportData = await this._fetchReportData(false);
            if (reportData) {
                this.showPopup('ReportPreviewPopup', {
                    title: this.env._t('X Report Preview'),
                    data: reportData,
                    confirm: (event) => this._onPrintReport(event)
                });
            }
        }

        async onClickZReport() {
            const reportData = await this._fetchReportData(true);
            if (reportData) {
                this.showPopup('ReportPreviewPopup', {
                    title: this.env._t('Z Report Preview'),
                    data: reportData
                }).then(({ confirmed, payload }) => {
                    if (confirmed && payload.is_z_report !== undefined) {
                        this._printReport(payload.is_z_report);
                    }
                });
            }
        }

        async _fetchReportData(is_z_report) {
            const session_id = this.env.pos.pos_session.id;
            const method = is_z_report ? 'get_z_report_data' : 'get_x_report_data';
            try {
                return await rpc.query({
                    model: 'pos.session',
                    method: method,
                    args: [[session_id]],
                });
            } catch (error) {
                const title = is_z_report ? this.env._t('Z Report Error') : this.env._t('X Report Error');
                const body = is_z_report ? this.env._t('Could not fetch Z report data.') : this.env._t('Could not fetch X report data.');
                this.showPopup('ErrorPopup', { title, body });
                return null;
            }
        }

        _onPrintReport({ detail }) {
             this._printReport(detail.is_z_report);
        }
    }
    XZReportButtons.template = 'XZReportButtons';

    ProductScreen.addControlButton({
        component: XZReportButtons,
        condition: function () {
            return true;
        },
    });

    Registries.Component.add(XZReportButtons);

    return XZReportButtons;
});
