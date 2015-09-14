(function() {
    require.config({
        paths: {
            jquery: 'lib/jquery.min',
            'jquery.modal': 'lib/jquery.modal.min',
            'jqueryRotate': 'jQueryRotate.2.2',
            'script': 'sep_script',
            tools: 'lib/modal.tools'
        },
        shim: {
            'jquery.modal': ['jquery'],
            'jquery.easing': ['jquery'],
            'jqueryRotate': ['jquery']
        }
    });
    require(['jquery', 'jqueryRotate', 'script', "tools"], function ($, jqueryRotate, easing, script, tool) {
        //关闭弹层
        function closeAlert(tp){
          tp.hide();
          $('#alert-page').hide();
        }
        $(".alert-close,.alert-btn").click(function(){
            closeAlert($(this).parents(".alert-box"));
        });
        //显示弹层
        function showAlert(obj){
            obj.show();
            $("#alert-page").show();
        }
        //注册领红包
        $(".receive-red").click(function(){
            alert(1);
            showAlert($(".no-new-user"));
        });
    });
})
