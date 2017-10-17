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
 * select/main.js -- Top-level select code.
 */

define([
    'jquery',
    'underscore',
    './data',
    './results',
    './languages',
    'select2/utils',
    'select2/dropdown',
    'select2/dropdown/search',
    'select2/dropdown/closeOnSelect',
    'select2/dropdown/attachBody',
    'select2/dropdown/minimumResultsForSearch',
    'select2/selection/eventRelay',
    'select2/selection/placeholder',
    'select2/selection/single',
    'select2/selection/multiple'
], function($, _, makeDataAdapter, makeResultsAdapter, Languages, Utils, Dropdown, DropdownSearch, CloseOnSelect, AttachBody, MinimumResultsForSearch, EventRelay, Placeholder, SingleSelection, MultipleSelection) {

  function initSelect(select) {
    select = $(select);

    var options = makeOptions(select);

    select.select2(options);
    focusInputAfterSelection(select, options);
    clearButtonHack(select, options);
    handleClear(select, options);

    addContainerClasses(select, options);
  }

  function makeOptions(select) {
    var options = {
      extraOptions: select.data('extraOptions'),
      placeholder: select.data('placeholder'),
      multiple: Boolean(select.prop('multiple'))
    };

    options = _.defaults(options, {
      extraOptions: [],
      theme: "amara",
      createTag: function(params) { return undefined; },
      minimumResultsForSearch: 8,
      escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
      templateResult: templateResult,
      templateSelection: templateSelection,
      language: {
        searching: function() { return gettext('Searching…');},
        loadingMore: function () { return gettext('Loading more results…'); },
        noResults: function () { return gettext('No results found');},
        inputTooShort: function (args) { return gettext('Start typing to search')}
      }
    });

    if (select.data('ajax')) {
      options.ajax = ajaxOptions(select);
      options.minimumResultsForSearch = 0;
      options.allowClear = !(select.data('clear') === false);
    } else if(select.data('languageOptions')) {
      options.data = Languages.languageChoiceData(select);
      options.type = 'language';
      options.allowClear = select.data('languageOptions').indexOf('null') > -1;
      options.tokenSeparators = [',', ' '];
    } else {
      var blankOptions = $('option', select).filter(function() {
        return !this.value;
      })
      options.allowClear = blankOptions.length > 0;
    }

    options = _.extend(options, {
      dataAdapter: makeDataAdapter(select, options),
      resultsAdapter: makeResultsAdapter(select, options),
      selectionAdapter: makeSelectionAdapter(select, options),
      dropdownAdapter: makeDropdownAdapter(select, options)
    });
    return options;
  }


  function ajaxOptions(select) {
    return {
      url: select.data('ajax'),
      dataType: 'json',
      delay: 250,
      data: function (params) {
        return {
          q: params.term, // search term
        };
      },
      cache: true
    };
  }

  function focusInputAfterSelection(select, options) {
    select.on('select2:close', function() {
      select.focus();
    });
  }


  function clearButtonHack(select, options) {
    // Workaround to prevent clicking the clear button from opening the dialog (see
    // http://stackoverflow.com/questions/29618382/disable-dropdown-opening-on-select2-clear#29688626)
    var unselecting = false;
    select.on('select2:unselecting', function() {
      unselecting = true;
    }).on('select2:opening', function(e) {
      if(unselecting) {
        unselecting = false;
        e.preventDefault();
      }
    });
  }

  function handleClear(select, options) {
    var clearOption = ['$clear', gettext('Clear')];
    if(options.allowClear) {
      select.on('select2:select', function(evt) {
        updateExtraOptions();
      }).on('select2:selecting', function(evt) {
        if(evt.params.args.data.id == '$clear') {
          if(options.multiple) {
            select.val([]).change();
          } else {
            select.val('').change();
          }
          select.select2('close');
          updateExtraOptions();
          evt.preventDefault();
        };
      });
      updateExtraOptions();
    }

    function updateExtraOptions() {
        var extraOptions = _.clone(options.extraOptions);
        if(select.val()) {
          // We can't create options with a blank id, so instead we use a special value and handle it in the selecting event
          extraOptions.push(clearOption);
        }
        select.trigger('data:updateExtraOptions', {
          extraOptions: extraOptions
        });
    }
  }

  function makeSelectionAdapter(select, options) {
    if(options.multiple) {
      var adapter = MultipleSelection;
    } else {
      var adapter = SingleSelection;
    }
    if (select.data('placeholder')) {
      adapter = Utils.Decorate(adapter, Placeholder);
    }
    adapter = Utils.Decorate(adapter, EventRelay);
    return adapter;
  }

  function makeDropdownAdapter(select) {
    var adapter = Dropdown;
    adapter = Utils.Decorate(adapter, DropdownSearch);
    adapter = Utils.Decorate(adapter, DropdownSearchPlaceholder);
    adapter = Utils.Decorate(adapter, MinimumResultsForSearch);
    adapter = Utils.Decorate(adapter, CloseOnSelect);
    adapter = Utils.Decorate(adapter, AttachBody);

    return adapter;
  }

  function DropdownSearchPlaceholder() { }
  DropdownSearchPlaceholder.prototype.render = function (decorated) {
    var $rendered = decorated.call(this);
    this.$search.data('placeholder', gettext('Start typing to search'));
    return $rendered;
  }

  function addContainerClasses(select, options) {
    var container = select.data('select2').$container;
    if(options.multiple) {
      container.addClass('multiple');
    }
    if(select.hasClass('border')) {
      container.addClass('border');
    }
  }

  function templateResult(data, container) {
    var text = _.escape(data.text);
    if(data.border) {
      $(container).addClass('select2-results__option--border');
    }
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


  $.behaviors('.select', initSelect);

});
