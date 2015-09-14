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
    require(['jquery', 'jqueryRotate', "tools"], function ($, jqueryRotate, tool) {
        //banner
        $("#banner").height($(window).height());
        //关闭弹层
        function closeAlert(tp){
          tp.hide();
          $('#alert-page').hide();
        }
        $(".alert-close,.close-per").click(function(){
            closeAlert($(this).parents(".alert-box"));
        });
        //显示弹层
        function showAlert(obj,txt){
            if(!txt){
               obj.find(".alert-cont").html(txt);
            }
            obj.show();
            $("#alert-page").show();
        }
        //注册领红包
        $(".receive-red").on('click',function(){
            showAlert($(".no-new-user"));
        });
        //充值
        $(".recharge").on("click",function(){
            showAlert($(".go-money"));
        });
        //理财
        $(".manage-money").on("click",function(){
            showAlert($(".running"));
        });
    });
}).call(this);
