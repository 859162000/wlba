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
        var activityId = 65;
        function ajaxFun(url,data,fn){
            $.ajax({
                type: "post",
                url: url,
                dataType: "json",
                data: data,
                async: false,
                success: function(data){
                    fn(data);
                }
            });
        }
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
        var funs = {
            "register": function(data){
                var ret_code = data.ret_code;
                if(ret_code == 00001){
                   showAlert($(".no-new-user"));
                }
            }
        }
        //注册领红包
        $(".receive-red").on('click',function(){
            ajaxFun(url,{"activity_id":activityId,"trigger_node":"register","action": "is_activity"},funs.register);
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
