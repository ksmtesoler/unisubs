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

(function($) {

$.behaviors('.lineConstrain', lineConstrain);

function lineConstrain(container) {
    container = $(container);
    container.visibilityChanged({
        callback: function(element, visible) {
           if (element[0].clientHeight < element[0].scrollHeight) {
               // your element have overflow
               element.addClass('constrained');
               constrain(element);
           } else {
               // your element doesn't have overflow
               element.removeClass('constrained');
           }
        },
        runOnLoad: false,
        frequency: 100
    });
}

function constrain(container) {
  container.on('click', function() {
    var sel = getSelection().toString();
    if(!sel){
      $(this).toggleClass('opened');
    }
  });
}

})(jQuery);