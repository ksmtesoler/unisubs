// require jquery and all plugins first, this way if other modules depend on jquery they will get the plugins too
require([
    'jquery',
    'jquery-behaviors',
    'jquery-form',
    'jquery-select2',
    'jScrollPane',
    // 'jScrollPane.mousewheel',
], function() {
    // require all the other modules
    require([
        // Third party libraries
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
        'selectList',
        'videoPage',
        'videoSubtitles',
        'fileUpload',
        'clamp',
        'styleGuide',
    ]);
});