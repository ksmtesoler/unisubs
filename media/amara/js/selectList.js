/*
 * Amara, universalsubtitles.org
 *
 * Copyright (C) 2016 Participatory Culture Foundation
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see
 * http://www.gnu.org/licenses/agpl-3.0.html.
 */

/*
 * selectList is used to handle a list of items connected to some popup forms.  When one or more items are selected, we pop open an actionBar. 
 * When one of the buttons on the actionBar is clicked, then we pop up a modal dialog.
 */


(function($) {
    $.behaviors('.selectList', selectList);
    $.behaviors('.selectAll', selectAll);
    $.behaviors('.deselectAll', deselectAll);

    function selectAll(checkbox) {
        checkbox = $(checkbox);
        var target = checkbox.data('target');
        var inputs = $(target).find('input[type="checkbox"]');

        checkbox.change(function() {
            checkbox.prop('checked') ?  inputs.prop('checked', true) : inputs.prop('checked', false);
            inputs.trigger('change');
        });
    }

    function deselectAll(button) {
        button = $(button);
        var target = button.data('target');
        var inputs = $(target).find('input[type="checkbox"]');

        button.click(function() {
            inputs.prop('checked', false);
            inputs.trigger('change');
        });
    }

    function selectList(list) {
        list = $(list);
        var actionBar = $(list.data('target'));
        var selection = $('.selectList-selection', actionBar);
        var checkboxes = list.find('input[type="checkbox"]');

        checkboxes.on('change', function() {
            checkboxes.is(':checked') ? actionBar.addClass('open') : actionBar.removeClass('open');
            selection.val(getSelection());
        });

        function getSelection() {
            var selection = [];
            checkboxes.filter(":checked").each(function() {
                selection.push(this.value);
            });
            return selection;
        }
    }
})(jQuery);
