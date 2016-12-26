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

$.behaviors('.select', initSelect);

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
    };

    if(select.attr('multiple') || hasEmptyValue(select)) {
        options.allowClear = true;
    }

    if(select.data('nosearchbox')) {
        options.minimumResultsForSearch = Infinity;
    } else {
        options.minimumResultsForSearch = 8;
    }

    if(select.data('languageOptions')) {
        options.data = languageChoiceData(select);
        if(select.data('languageOptions').indexOf('null') != -1) {
            options.allowClear = true;
        }
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

function languageChoiceData(select) {
    var data = [];
    var enabledSelections = select.data('languageOptions').split(" ");
    var exclude = select.data('exclude');
    var limitTo = select.data('limitTo');
    var choiceMaker = new LanguageChoiceMaker(initial, exclude, limitTo);

    if(select.data('initial')) {
        var initial = select.data('initial').split(':');
    } else {
        var initial = [];
    }

    function sectionEnabled(name) {
        return enabledSelections.indexOf(name) > -1;
    }
    if(sectionEnabled('null')) {
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

            choices.push({
                id: code,
                text: getLanguageName(code),
                selected: _.contains(self.initial, code)
            });
            self.alreadyAdded[code] = true;
        });
        return choices;
    }
};

function languageChoice(code) {
    return { id: code, text: getLanguageName(code), selected: code == this };
}

})(jQuery);
