odoo.define('bsr_treasury_forecast.TreasuryChartWidget', function (require) {
    "use strict";

    const AbstractField = require('web.AbstractField');
    const fieldRegistry = require('web.field_registry');
    const core = require('web.core');
    const qweb = core.qweb;

    const TreasuryChartWidget = AbstractField.extend({
        template: 'TreasuryChart',

        start: function () {
            this._super.apply(this, arguments);
            this.chart = null;
        },

        _render: function () {
            this.$el.html(qweb.render(this.template, {widget: this}));
            this._renderChart();
        },

        _renderChart: function () {
            const self = this;
            const data = this.record.data.line_ids.map(function (line) {
                return {
                    x: line.data.date,
                    y: line.data.amount,
                };
            });

            if (this.chart) {
                this.chart.destroy();
            }

            this.chart = new Chart(this.$('.o_treasury_chart'), {
                type: 'line',
                data: {
                    datasets: [{
                        label: 'Treasury Forecast',
                        data: data,
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                    }],
                },
                options: {
                    scales: {
                        xAxes: [{
                            type: 'time',
                            time: {
                                unit: 'day',
                            },
                        }],
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                            },
                        }],
                    },
                },
            });
        },
    });

    fieldRegistry.add('treasury_chart', TreasuryChartWidget);

    return TreasuryChartWidget;
});
