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
            try {
                const session_id = this.env.pos.pos_session.id;
                // This is a placeholder for the X report logic
                await this.env.pos.do_action('bsr_xz_report.action_report_pos_x', {
                    additional_context: {
                        active_ids: [session_id],
                    },
                });
            } catch (error) {
                this.showPopup('ErrorPopup', {
                    title: this.env._t('X Report Error'),
                    body: this.env._t('Could not generate the X report.'),
                });
            }
        }

        async onClickZReport() {
            try {
                const session_id = this.env.pos.pos_session.id;
                await rpc.query({
                    model: 'pos.session',
                    method: 'generate_z_report',
                    args: [session_id],
                });

                 await this.env.pos.do_action('bsr_xz_report.action_report_pos_z', {
                    additional_context: {
                        active_ids: [session_id],
                    },
                });
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
