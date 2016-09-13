$(function () {
  $('[data-toggle="tooltip"]').tooltip()
});

$(document).on('ready', function(){

  // Select / Autofill
  $('.select_autofill').select2({
    theme: "bootstrap"
  });

  // Collapsible / Constrained content
  $('.constrain').on('click', function() {
    $(this).addClass('opened');
  });

  $('[data-href]').on('click', function(e) {
    e.preventDefault();
    var href = $(this).attr('data-href');
    window.location.href = href;
  });
  $('[data-toggle="popover"]').popover();
});
