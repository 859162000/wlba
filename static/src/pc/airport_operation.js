(function(){
    require.config({
        paths: {
            jquery : 'lib/jquery.min',
            'jquery.modal': 'lib/jquery.modal.min',
            tools: 'lib/modal.tools'
        },
        shim: {
            'jquery.model': ["jquery"]
        }
    })
    require(['jquery'],function($){
        alert(1)
    })



}).call(this);