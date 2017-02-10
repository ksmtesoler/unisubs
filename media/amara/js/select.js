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

define(['jquery'], function($) {

$.fn.select2.amd.require([
    'jquery',
    'select2/data/ajax',
    'select2/utils',
    'select2/data/minimumInputLength',
    'select2/dropdown',
    'select2/dropdown/search',
    'select2/dropdown/closeOnSelect',
    'select2/dropdown/attachBody',
], function($, AjaxData, Utils, MinimumInputLength, Dropdown, DropdownSearch, CloseOnSelect, AttachBody) {

$(function() {
    $.behaviors('.select', initSelect);
});

function arrayToMap(array) {
    var map = {};
    _.each(array, function(val) { map[val] = true; });
    return map;
}

function hasEmptyValue(select) {
    return $('option', select).is(function (i, opt) {
        return opt.value == "";
    });
}

function initSelect(select) {
    select = $(select);
    var options = {
        theme: "bootstrap",
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        templateResult: templateResult,
        templateSelection: templateSelection,
        language: {
            searching: function() { return gettext('Searching…');},
            loadingMore: function () { return gettext('Loading more results…'); },
            noResults: function () { return gettext('No results found');},
            inputTooShort: function (args) { return gettext('Start typing to search')}
        }
    };

    if (select.attr('placeholder')) {
        options.placeholder = select.attr('placeholder');
    }
    if(select.attr('multiple') || hasEmptyValue(select)) {
        options.allowClear = true;
    }

    if(select.data('nosearchbox')) {
        options.minimumResultsForSearch = Infinity;
    } else if(!select.data('ajax')) {
        options.minimumResultsForSearch = 8;
    }

    if(select.data('languageOptions')) {
        options.data = languageChoiceData(select);
        if(select.data('languageOptions').indexOf('null') != -1) {
            options.allowClear = true;
        }
    }

    if(select.data('ajax')) {
        _.extend(options, ajaxOptions(select));
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

    addContainerClasses(select, options);
}

function addContainerClasses(select, options) {
    var container = select.data('select2').$container;
    if(select.attr('multiple')) {
        container.addClass('multiple');
    }
    if(select.hasClass('border') || options.ajax) {
        container.addClass('border');
    }
    if(options.ajax) {
        container.addClass('searchbar');
    }
}

function templateResult(data) {
    var text = _.escape(data.text);
    if(data.avatar) {
        return data.avatar + text;
    } else {
        return text;
    }
}

function templateSelection(data) {
    var text = _.escape(data.text);
    return text;
}
function ajaxOptions(select) {
    var dropdownAdapter = Utils.Decorate(Dropdown, DropdownSearch);
    dropdownAdapter = Utils.Decorate(dropdownAdapter, DropdownExtraOptions);
    dropdownAdapter = Utils.Decorate(dropdownAdapter, CloseOnSelect);
    dropdownAdapter = Utils.Decorate(dropdownAdapter, AttachBody);

    return {
        ajax: {
          url: select.data('ajax'),
          dataType: 'json',
          delay: 250,
          data: function (params) {
            return {
              q: params.term, // search term
            };
          },
          processResults: function(data, params) {
              return data
          },
          cache: true
        },
        dropdownAdapter: dropdownAdapter,
        minimumInputLength: 1
    };
}

function DropdownExtraOptions(decorated, element, options) {
    this.extraOptions = element.data('extraOptions');
    this.element = element;
    decorated.call(this, element, options);
}

DropdownExtraOptions.prototype.render = function (decorated) {
    var rendered = decorated.call(this);
    var results = $('.select2-results', rendered);
    var choices = results.wrap('<span class="select2-choices">').parent();
    if(this.extraOptions) {
        choices.append(this.makeExtraOptions());
    }
    return rendered;
}

DropdownExtraOptions.prototype.makeExtraOptions = function (decorated) {
    var self = this;
    var select = this.element;
    var extraOptions = $('<ul>', {
        "class": "select2-extraoptions",
        "role": "tree",
        "aria-hidden": false,
        "aria-expanded": true,
    });
    var currentValue = select.val();
    _.each(this.extraOptions, function(option) {
        var data = {
            id: option[0],
            text: option[1]
        };
        var li = $('<li>', {
            "class": "select2-extraoptions__option",
            "role": "treeitem",
            "aria-live": "assertive",
            "aria-selected": data.id == currentValue
        }).html(templateResult(data));
        extraOptions.append(li);
        li.hover(function() {
            li.addClass("select2-extraoptions__option--highlighted");
        }, function() {
            li.removeClass("select2-extraoptions__option--highlighted");
        }).on('click', function() {
            select.val(data.id);
            self.trigger('select', {
                data: data
            });
        });
        select.on('change', function() {
            li.attr('aria-selected', select.val() == data.id);
        });
    });
    return extraOptions;
}

function languageChoiceData(select) {
    var data = [];
    var enabledSelections = select.data('languageOptions').split(" ");
    var exclude = select.data('exclude');
    var limitTo = select.data('limitTo');

    if(select.data('initial')) {
        var initial = select.data('initial').split(':');
    } else {
        var initial = [];
    }

    var choiceMaker = new LanguageChoiceMaker(initial, exclude, limitTo);

    function sectionEnabled(name) {
        return enabledSelections.indexOf(name) > -1;
    }
    if(sectionEnabled('null') && !select.attr('multiple')) {
        data.push({
            id: '',
            selected: _.contains(initial, '')
        });
    }
    if(sectionEnabled('my')) {
        data.push({
            text: gettext('My Languages'),
            children: choiceMaker.makeChoices(userLanguages)
        });
    }
    if(sectionEnabled('popular')) {
        data.push({
            text: gettext('Popular Languages'),
            children: choiceMaker.makeChoices(popularLanguages)
        });
    }
    if(sectionEnabled('all')) {
        data.push({
            text: gettext('All Languages'),
            children: choiceMaker.makeChoices(allLanguages)
        });
    }
    return data;
}

function LanguageChoiceMaker(initial, exclude, limitTo) {
    this.initial = initial;
    if(exclude === undefined) {
        exclude = [];
    }
    if(limitTo === undefined) {
        limitTo = [];
        limitToEnabled = false;
    } else {
        limitToEnabled = true;
    }
    this.exclude = arrayToMap(exclude);
    this.limitTo = arrayToMap(limitTo);
    this.alreadyAdded = {};
}

LanguageChoiceMaker.prototype = {
    makeChoices: function(languages) {
        var choices = [];
        var self = this;
        _.each(languages, function(code) {
            if(self.alreadyAdded[code] || self.exclude[code] ||
                (self.limitToEnabled && !self.limitTo[code])) {
                return;
            }
            var choice = {
                id: code,
                text: getLanguageName(code)
            };
            if(_.contains(self.initial, code)) {
                choice.selected = 'selected';
            }
            choices.push(choice);
            self.alreadyAdded[code] = true;
        });
        return choices;
    }
};

function languageChoice(code) {
    return { id: code, text: getLanguageName(code), selected: code == this };
}

});

});
