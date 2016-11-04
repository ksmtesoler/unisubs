// Open forms with content from an AJAX request

(function($) {
    $.behaviors('.openAjaxModal', openAjaxModal);

    function openAjaxModal(button) {
        // FIXME: we should consilidate this code with the ajaxform code
        var button = $(button);

        function showModal(content) {
            var modal = $(content);
            $(document.body).append(modal);
            modal.updateBehaviors();
            modal.modal().on('hidden.bs.modal', function() {
                modal.remove();
            });
            $('form', modal).ajaxForm({
                success: function (data, textStatus, xhr) {
                    if(xhr.getResponseHeader('X-Form-Success')) {
                        window.location.reload();
                    } else {
                        modal.modal('hide');
                        showModal(data);
                    }
                }
            });
        }

        function getFormQuery() {
            var query = getQueryParams();
            var buttonData = button.data();
            if(buttonData.form) {
                query.form = buttonData.form;
            }
            if(buttonData.selection) {
                query.selection = buttonData.selection;
            }
            return query;
        }

        button.click(function() {
            var url = window.location.pathname + '?' + $.param(getFormQuery());
            $.ajax(url, {
                success: function(data) {
                    showModal(data);
                }
            });
        });
    }
})(jQuery);
