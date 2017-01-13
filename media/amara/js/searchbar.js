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

// TB: This is an example based on zero knowledge of the actual Amara API or how this searchbar is going to be used beyond a general search for members?

(function($) {

$.behaviors('.searchbar', initSearch);

function formatMemberSelection (member) {
  return member.full_name || member.text;
}
function formatMember (member) {
  if (member.loading) return member.text;

  var markup = "<span class='avatar avatar-"+ member.avatar_color +"'></span>" + member.full_name;
  return markup;
}

function initSearch(container) {
    select = $(container).find('select');
    var options = {
        theme: "bootstrap",
        ajax: {
          url: "/media/data/members.json",
          dataType: 'json',
          delay: 250,
          data: function (params) {
            return {
              q: params.term, // search term
              page: params.page
            };
          },
          processResults: function (data, params) {
            // parse the results into the format expected by Select2
            // since we are using custom formatting functions we do not need to
            // alter the remote JSON data, except to indicate that infinite
            // scrolling can be used
            params.page = params.page || 1;

            return {
              results: data.items,
              pagination: {
                more: (params.page * 30) < data.total_count
              }
            };
          },
          cache: true
        },
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        minimumInputLength: 1,
        templateResult: formatMember,
        templateSelection: formatMemberSelection
    };

    if (select.attr('placeholder')) {
        options.placeholder = select.attr('placeholder');
    }
    if(select.attr('multiple')) {
        options.allowClear = true;
    }

    select.select2(options);
    // Workaround to prevent clicking the clear button from opening the dialog (see
    // http://stackoverflow.com/questions/29618382/disable-dropdown-opening-on-select2-clear#29688626)
    select.on('select2:unselecting', function() {
        $(this).data('unselecting', true);
    }).on('select2:opening', function(e) {
        if ($(this).data('unselecting')) {
            $(this).removeData('unselecting');
            e.preventDefault();
        }
    });
}

})(jQuery);
