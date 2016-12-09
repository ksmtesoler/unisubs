$(function () {
  $('[data-toggle="tooltip"]').tooltip();
  $('[data-toggle="popover"]').popover();
});

$(document).on('ready', function(){

  // Collapsible / Constrained content
  $('.constrain').on('click', function() {
    $(this).addClass('opened');
  });

  $('[data-href]').on('click', function(e) {
    e.preventDefault();
    var href = $(this).attr('data-href');
    window.location.href = href;
  });

});
