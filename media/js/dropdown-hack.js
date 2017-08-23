$(function() {
    $('.dropdown-toggle').click(function() {
        var link = $(this);
        var dropdown = link.closest('.dropdown');
        if(dropdown.hasClass('open')) {
            dropdown.removeClass('open');
            link.attr("aria-expanded", "false");
        } else {
            dropdown.addClass('open');
            link.attr("aria-expanded", "true");
        }
    });
});
