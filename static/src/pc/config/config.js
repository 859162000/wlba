
require.config({
    baseUrl: '/static/scripts/pc/',
    paths: {
        'jquery': 'lib/jquery.min',
        'jquery.animateNumber': 'lib/jquery.animateNumber.min',
        'countdown': 'model/countdown',
        'jquery.fullPage': 'lib/jquery.fullPage.min',
        'videojs': 'lib/video.min',
        'jquery.placeholder': 'lib/jquery.placeholder',
        'jquery.modal': 'lib/jquery.modal.min',
        'tools': 'lib/modal.tools',
        'csrf': 'model/csrf'
    },

    shim: {
        'jquery.animateNumber': ['jquery'],
        'jquery.modal': ['jquery'],
        'jquery.fullPage': ['jquery'],
        'jquery.placeholder': ['jquery']
    }
});
