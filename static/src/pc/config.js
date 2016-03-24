require.config({
    baseUrl: '/static/src/pc/',
    paths: {
        'jquery': 'lib/jquery.min',
        'jquery.modal': 'lib/jquery.modal.min',
        'tools': 'lib/modal.tools',
        'csrf' : 'model/csrf',
        'jquery.validate': 'lib/jquery.validate.min',
        'jquery.zclip': 'lib/jquery.zclip.min',
        'picker': 'lib/picker',
        'picker.date': 'lib/picker.date',
        'echarts': 'lib/echarts.min',
    },
    shim: {
        'jquery.modal': ['jquery'],
        'jquery.validate': ['jquery'],
        'jquery.zclip': ['jquery'],
        'picker.date': ['jquery'],
        'picker': ['jquery'],
    }
});