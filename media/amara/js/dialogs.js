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

//
// dialags.js -- Dialog code


(function($) {
    var currentModal = null;

    // FIXME: Currently we expose a global function, but should we use a JS
    // module instead like JQuery/underscore?

    // show/replace the our modal dialog
    showModal = function(content) {
        content = $(content);
        if(currentModal) {
            currentModal.empty().append(content);
        } else {
            currentModal = $('<div class="modal fade" tabindex="-1" role="dialog"></div>').append(content);
            currentModal.append(content);
            $(document.body).append(currentModal);
            currentModal.modal().on('hidden.bs.modal', function() {
                currentModal.remove();
                currentModal = null;
            });
        }
        return currentModal;
    }
})(jQuery);


