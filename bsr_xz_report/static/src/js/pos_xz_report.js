odoo.define('bsr_xz_report.pos_xz_report', function (require) {
    "use strict";

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');

    class XZReportButtons extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click-x-report', this.onClickXReport);
            useListener('click-z-report', this.onClickZReport);
        }

        async onClickXReport() {
            const session_id = this.env.pos.pos_session.id;
            try {
                const report_action = await rpc.query({
                    model: 'pos.session',
                    method: 'generate_x_report',
                    args: [[session_id]],
                });
                if (report_action) {
                    this.env.pos.do_action(report_action);
                }
            } catch (error) {
                this.showPopup('ErrorPopup', {
                    title: this.env._t('X Report Error'),
                    body: this.env._t('Could not generate the X report.'),
                });
            }
        }

        async onClickZReport() {
            const session_id = this.env.pos.pos_session.id;
            try {
                const report_action = await rpc.query({
                    model: 'pos.session',
                    method: 'generate_z_report',
                    args: [[session_id]],
                });
                if (report_action) {
                    this.env.pos.do_action(report_action);
                }
            } catch (error) {
                this.showPopup('ErrorPopup', {
                    title: this.env._t('Z Report Error'),
                    body: this.env._t('Could not generate the Z report. Make sure the session is closed.'),
                });
            }
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
