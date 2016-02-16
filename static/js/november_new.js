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
        var activityId = 86; //activity id l:38 s:98 w:86
        var payId = 86;
        function ajaxFun(url,data,fn,err){
            $.ajax({
                type: "get",
                url: url,
                dataType: "json",
                data: data,
                async: false,
                success: function(data){
                    fn(data);
                },
                error: function(){
                    if(err != undefined){
                       err();
                    }

                }
            });
        }
        //banner
        function telBan(){
            var banDom = $("#banner");
            var winh = $(window).height();
            if(!banDom.hasClass("pc-banner")){
                //if(winh < 1056){
                //    banDom.addClass("min-banner");
                //}
                banDom.height(winh);
            }
        }
        telBan();
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
            "register": function(data){
                var ret_code = data.ret_code;
                //console.log(data,"register");
                if(ret_code === "10001" || ret_code === "00001"){
                    showAlert($(".running"));
                }else{
                    showAlert($(".no-new-user"),"Sorry~您不符合参加规则");
                }
            },
            "validation": function(data){
                var ret_code = data.ret_code;
                //console.log(data,"register");
                if(ret_code === "10001" || ret_code === "00001"){
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
                }else if(ret_code === "10001" || ret_code === "00001"){
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
                }else if(ret_code === "10001" || ret_code === "00001"){
                    showAlert($(".running"));
                }else{
                    showAlert($(".no-new-user"),"Sorry~您不符合参加规则");
                }
            },
            "validationErr": function(){
                window.open("/accounts/register/?next=/accounts/register/first/");
            },
            "rechargeErr": function(){
                window.open("/accounts/register/?next=/pay/banks/");
            }
        };
        //注册领红包
        $(".receive-red").on('click',function(){
            //ajaxFun("/api/activity/joinInfo/",{"activity_id":activityId,"trigger_node":"validation"},funs.validation);
            ajaxFun("/api/activity/joinInfo/",{"activity_id":activityId,"trigger_node":"register"},funs.register);
        });
        //实名
        $(".for-name").on("click",function(){
            ajaxFun("/api/activity/joinInfo/",{"activity_id":activityId,"trigger_node":"validation"},funs.validation,funs.validationErr);
        });
        //充值
        $(".recharge").on("click",function(){
            ajaxFun("/api/activity/joinInfo/",{"activity_id":payId,"trigger_node":"first_pay"},funs.firstPay,funs.rechargeErr);
        });
        //理财
        $(".manage-money").on("click",function(){
            ajaxFun("/api/activity/joinInfo/",{"activity_id":payId,"trigger_node":"first_buy"},funs.firstBuy);
        });

        //返回顶部
        function backTop(){
          $('body,html').animate({scrollTop: 0}, 600);
        }
        var topDom = $("a.xl-backtop");
        var backDom = topDom.parents("div.backtop");
        function showDom(){
          if ($(document).scrollTop() > 0) {
            backDom.addClass("show-backtop");
          } else if ($(document).scrollTop() <= 0) {
            backDom.removeClass("show-backtop");
          }
        }
        showDom();
        $(window).scroll(function () {
        showDom();
        });

        topDom.on('click',function(){
          backTop();
          return false
        });
    });
}).call(this);
