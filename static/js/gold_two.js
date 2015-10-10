(function() {
    require.config({
        paths: {
            jquery: 'lib/jquery.min',
            'jquery.modal': 'lib/jquery.modal.min',
            'jqueryRotate': 'jQueryRotate.2.2',
            tools: 'lib/modal.tools'
        },
        shim: {
            'jquery.modal': ['jquery'],
            'jquery.easing': ['jquery'],
            'jqueryRotate': ['jquery']
        }
    });
    require(['jquery'], function ($) {
        $("#click-prompt").click(function(){
            var dom = $("#click-info");
            if(dom.is(":hidden")){
              dom.stop(true,true).slideDown(200);
            }else{
              dom.stop(true,true).slideUp(200);
            }
        });
    });
}).call(this);
