(function($) {
$.behaviors('.clamp', clamp);

function clamp(container) {
    container = $(container);

    $(window).resize(checkOverflow);
    $(document).on("contentUpdate", checkOverflow);
    checkOverflow();

    $('.clamp-expand', container).click(function() {
        container.addClass('expanded');
    });
    $('.clamp-collapse', container).click(function() {
        container.removeClass('expanded');
    });

    function checkOverflow() {
        if(container.hasClass('expanded')) {
            return;
        }
        var overflowing = false;
        $('.clamp-lines', container).each(function() {
            if (this.clientHeight < this.scrollHeight) {
                overflowing = true;
            }
        });
        if($('.clamp-list li:hidden', container).length > 0) {
            overflowing = true;
        }
        if(overflowing) {
            container.addClass('overflowing');
        } else {
            container.removeClass('overflowing');
        }
    }
}

})(jQuery);
