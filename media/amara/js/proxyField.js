(function($) {
    $.behaviors('.proxyField', proxyField);

    function proxyField(container) {
        var container = $(container);
        var realField = $(container.data('proxyFor'));
        $(':input', container).change(updateRealField);
        if(!container.hasClass('deferUpdate')) {
            $('input[type=text], textarea', container).keyup(updateRealField);
        }
        function updateRealField() {
            var newVal = $(this).val();
            if(newVal != realField.val()) {
                realField.val($(this).val());
                realField.trigger('change');
            }
        }
    }
})(jQuery);

