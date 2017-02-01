(function($) {
$(document).ready(function() {

    $.behaviors('.lineClamp', lineClamp);
    $.behaviors('.clamp-toggle', clampToggle);

    function lineClamp(elt) {
        elt = $(elt);
        checkOverflow();

        function checkOverflow() {
            if(elt.hasClass('expanded')) {
                return;
            }
            if (elt.height() < elt.prop('scrollHeight')) {
                elt.addClass('overflowing');
            } else {
                elt.removeClass('overflowing');
            }
        }

        $(window).resize(checkOverflow);
        $(document).on("contentUpdate", checkOverflow);
    }

    function clampToggle(elt) {
        elt = $(elt);
        var lineClamper = $(elt.data('target'));
        var origText = $(elt).text();

        elt.click(function() {
            if(lineClamper.hasClass('expanded')) {
                lineClamper.removeClass('expanded');
                elt.text(origText);
            } else {
                lineClamper.addClass('expanded');
                elt.text(elt.data('altText'));
            }
        });
    }
});

})(jQuery);
