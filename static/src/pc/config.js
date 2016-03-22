require.config({
    baseUrl: '/static/src/pc/',
    paths: {
        'jquery': 'lib/jquery.min',
        'jquery.modal': 'lib/jquery.modal.min',
        'tools': 'lib/modal.tools',
        'csrf' : 'model/csrf',
        'jquery.validate': 'lib/jquery.validate.min',
        'jquery.zclip': 'lib/jquery.zclip.min'
    },
    shim: {
        'jquery.modal': ['jquery'],
        'jquery.validate': ['jquery'],
        'jquery.zclip': ['jquery']
    }
});