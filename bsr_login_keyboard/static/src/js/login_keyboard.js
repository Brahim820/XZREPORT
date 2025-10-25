odoo.define('bsr_login_keyboard.keyboard', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    var qweb = require('web.core').qweb;

    publicWidget.registry.BsrLoginKeyboard = publicWidget.Widget.extend({
        selector: '#keyboard',

        start: function () {
            var self = this;
            this.focusedInput = null;

            this.$el.html(qweb.render('bsr_login_keyboard.keyboard_template'));

            $('input[name="login"], input[name="password"]').on('focus', function () {
                self.focusedInput = $(this);
            });

            this.$el.on('click', '.keyboard-key', function () {
                if (!self.focusedInput) {
                    return;
                }

                var key = $(this).data('key');

                if (key === 'backspace') {
                    var currentValue = self.focusedInput.val();
                    self.focusedInput.val(currentValue.substring(0, currentValue.length - 1));
                } else {
                    self.focusedInput.val(self.focusedInput.val() + key);
                }
            });

            return this._super.apply(this, arguments);
        },
    });
});
