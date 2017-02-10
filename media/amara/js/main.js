// require jquery and all plugins first, this way if other modules depend on jquery they will get the plugins too
require([
    'jquery',
    'jquery-behaviors',
    'jquery-form',
    'select2',
    'jScrollPane',
    'jScrollPane.mousewheel',
], function() {
    // require all the other modules
    require([
        // Third party libraries
        'underscore',
        'bootstrap',
        'chartist',
        'chartist-plugin-tooltip',
        // Amara modules
        'ajax',
        'dialogs',
        'proxyField',
        'dependentSelect',
        'select',
        'scrollBars',
        'querystring',
        'selectList',
        'videoPage',
        'videoSubtitles',
        'fileUpload',
        'clamp',
        'main',
        'styleGuide',
    ]);
});
