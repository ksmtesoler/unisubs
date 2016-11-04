// Simple ajax form implementation

(function($) {
    $.behaviors('.ajaxForm', ajaxForm);

    function ajaxForm(form) {
        var submitting = false;
        var sawSecondSubmit = false;
        form = $(form);
        form.ajaxForm({
            beforeSubmit: function() {
                if(submitting) {
                    sawSecondSubmit = true;
                    return false;
                }
                submitting = true;
                if(form.hasClass('updateLocation')) {
                    history.pushState(null, "", window.location.protocol + "//" + window.location.host +
                            window.location.pathname + '?' + form.formSerialize());
                }
            },
            complete: function() {
                submitting = false;
                if(sawSecondSubmit) {
                    sawSecondSubmit = false;
                    form.submit();
                }
            },
            success: function(data, statusText, xhr) {
                if(data && data.replace) {
                    $.each(data.replace, function(selector, html) {
                        var newContent = $(html);
                        var container = $(selector);
                        container.empty().append(newContent);
                        container.updateBehaviors();
                        if(data.clearForm) {
                            $(form).clearForm();
                        }
                        if(data.hideModal) {
                            $.each(data.hideModal, function(i, selector) {
                                $(selector).modal('hide');
                            });
                        }
                    });
                }
            }
        });

        if(form.hasClass('updateOnChange')) {
            $(':input', form).change(submitIfChanged);
            $('input[type=text]', form).keyup(submitIfChanged);
        }

        var lastSerialize = form.formSerialize();
        function submitIfChanged() {
            var newSerialize = form.formSerialize();
            if(newSerialize != lastSerialize) {
                lastSerialize = newSerialize;
                form.submit();
            }
        }
    }


    function openModalButton(button) {
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
