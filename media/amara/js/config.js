require.config({
    paths: {
        'underscore': 'lib/underscore/underscore',
        'jquery': 'lib/jquery/dist/jquery',
        'jquery-behaviors': 'lib/jquery-behaviors/behaviors',
        'jquery-form': 'lib/jquery-form/jquery.form',
        'bootstrap': 'lib/bootstrap/dist/js/bootstrap',
        'jScrollPane': 'lib/jScrollPane/script/jquery.jscrollpane',
        'jScrollPane.mousewheel': 'lib/jScrollPane/script/jquery.mousewheel',
        'select2': 'lib/select2/src/js/select2',
        'jquery-select2': 'lib/select2/src/js/jquery.select2',
        'jquery-mousewheel': 'lib/select2/src/js/jquery.mousewheel.shim',
        'chartist': 'lib/chartist/dist/chartist',
        'chartist-plugin-tooltip': 'lib/chartist-plugin-tooltip/dist/chartist-plugin-tooltip',
    },
    shim: {
        'jquery-behaviors': ['jquery'],
        'jquery-form': ['jquery'],
        'bootstrap': ['jquery'],
        'jScrollPane': ['jquery'],
        'jScrollPane.mousewheel': ['jquery'],
        'jquery-select2': ['jquery'],
    }
});
