(function($) {
    $.behaviors('.videoSubtitles-revisions', subtitleRevisions);

    function subtitleRevisions(section) {
        var checkboxes = $('input[type=checkbox]', section);
        var compareLink = $('.videoSubtitles-compare', section);

        updateCompareLink();

        checkboxes.change(function() {
            // allow no more than 2 checkboxes to be checked at once
            if(this.checked && checkboxes.filter(':checked').length > 2) {
                this.checked = false;
            }
            updateCompareLink();
        });

        function updateCompareLink() {
            var checked = checkboxes.filter(':checked');
            if(checked.length == 2) {
                var id1 = checked.eq(0).data('id');
                var id2 = checked.eq(1).data('id');
                var url = compareLink.data('urlTemplate').replace(/111\/222\/$/, id1 + '/' + id2 + '/');
                compareLink.attr("href", url);
            } else {
                compareLink.attr("href", "#");
            }
        }
    }

})(jQuery);


