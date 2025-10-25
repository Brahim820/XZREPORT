odoo.define('bsr_login_keyboard.keyboard', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    var qweb = require('web.core').qweb;

    publicWidget.registry.BsrLoginKeyboard = publicWidget.Widget.extend({
        selector: '#keyboard',

        start: function () {
            var self = this;
            this.focusedInput = null;
            this.shift = false;

            this.$el.html(qweb.render('bsr_login_keyboard.keyboard_template'));

            $('input[name="login"], input[name="password"]').on('focus', function () {
                self.focusedInput = $(this);
            });

            this.$el.on('click', '.keyboard-key', function (e) {
                var key = $(e.currentTarget).data('key');

                if (key === 'shift') {
                    self.shift = !self.shift;
                    self._toggleShift();
                    return;
                }

                if (!self.focusedInput) {
                    return;
                }

                if (key === 'backspace') {
                    var currentValue = self.focusedInput.val();
                    self.focusedInput.val(currentValue.substring(0, currentValue.length - 1));
                } else {
                    var character = self.shift ? key.toUpperCase() : key;
                    self.focusedInput.val(self.focusedInput.val() + character);
                }
            });

            return this._super.apply(this, arguments);
        },

        _toggleShift: function () {
            if (this.shift) {
                this.$('.lower').hide();
                this.$('.upper').show();
                this.$('.shift').addClass('active');
            } else {
                this.$('.upper').hide();
                this.$('.lower').show();
                this.$('.shift').removeClass('active');
            }
        },
    });
});
