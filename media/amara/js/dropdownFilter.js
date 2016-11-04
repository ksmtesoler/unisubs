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

$.behaviors('.dropdownFilter', dropdownFilter);

function dropdownFilter(select) {
    select = $(select);
    var options = {
        theme: "bootstrap",
    };

    if(select.data('languageOptions')) {
        options.data = languageChoiceData(select);
    }
    if(select.data('nosearchbox')) {
        options.minimumResultsForSearch = Infinity;
    } else {
        options.minimumResultsForSearch = 8;
    }
    select.select2(options);
}

function languageChoiceData(select) {
    var data = [];
    var enabledSelections = select.data('languageOptions').split(" ");
    var initial = select.data('initial');
    var nullLabel = select.data('languageNullLabel') || gettext('Any language');
    var choiceMaker = new LanguageChoiceMaker(initial);

    function sectionEnabled(name) {
        return enabledSelections.indexOf(name) > -1;
    }
    if(sectionEnabled('null')) {
        if(select.data("placeholder")) {
            data.push({
                id: '',
                selected: initial == '',
            });
        } else {
            data.push({
                id: 'X',
                text: nullLabel,
                selected: initial == 'X'
            });
        }
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

function LanguageChoiceMaker(initial) {
    this.initial = initial;
    this.alreadyAdded = {};
}

LanguageChoiceMaker.prototype = {
    makeChoices: function(languages) {
        var choices = [];
        var self = this;
        _.each(languages, function(code) {
            if(!self.alreadyAdded[code]) {
                choices.push({
                    id: code,
                    text: getLanguageName(code),
                    selected: code == self.initial
                });
                self.alreadyAdded[code] = true;
            }
        });
        return choices;
    }
};

function languageChoice(code) {
    return { id: code, text: getLanguageName(code), selected: code == this };
}

})(jQuery);
