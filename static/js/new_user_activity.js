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
        var activityId = 65; //activity id l:37 65
        function ajaxFun(url,data,fn){
            $.ajax({
                type: "get",
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
        var banDom = $("#banner");
        var winh = $(window).height();
        banDom.height(winh);
        if(winh < 970){
            banDom.addClass("min-banner");
        }
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
            if(txt){
               obj.find(".alert-cont").html(txt);
            }
            obj.show();
            $("#alert-page").show();
        }
        var funs = {
            "validation": function(data){
                var ret_code = data.ret_code;
                //console.log(data,"register");
                if(ret_code === "10000"){
                    showAlert($(".running"));
                }else if(ret_code === "00000") {
                    showAlert($(".to-realName"));
                }else{
                    showAlert($(".no-new-user"),"Sorry~您不符合参加规则");
                }
            },
            "firstPay": function(data){
                var ret_code = data.ret_code;
                //console.log(data,"firstPay");
                if(ret_code === "00002"){
                    showAlert($(".go-money"));
                }else if(ret_code === "10000"){
                    showAlert($(".running"));
                }else{
                    showAlert($(".no-new-user"),"Sorry~您不符合参加规则");
                }
            },
            "firstBuy": function(data){
                var ret_code = data.ret_code;
                //console.log(data,"firstBuy");
                if(ret_code === "00002"){
                    showAlert($(".to-invest"));
                }else if(ret_code === "10000"){
                    showAlert($(".running"));
                }else{
                    showAlert($(".no-new-user"),"Sorry~您不符合参加规则");
                }
            }
        }
        //注册领红包
        $(".receive-red").on('click',function(){
            ajaxFun("/api/activity/joinInfo/",{"activity_id":activityId,"trigger_node":"validation"},funs.validation);
        });
        //充值
        $(".recharge").on("click",function(){
            ajaxFun("/api/activity/joinInfo/",{"activity_id":activityId,"trigger_node":"first_pay"},funs.firstPay);
        });
        //理财
        $(".manage-money").on("click",function(){
            ajaxFun("/api/activity/joinInfo/",{"activity_id":activityId,"trigger_node":"first_buy"},funs.firstBuy);
        });
    });
}).call(this);
