require.config({
    baseUrl: '/static/src/pc/',
    paths: {
        'jquery': 'lib/jquery.min',
        'jquery.modal': 'lib/jquery.modal.min',
        'tools': 'lib/modal.tools',
        'csrf' : 'model/csrf'
    },
    shim: {
        'jquery.modal': ['jquery']
    }
});