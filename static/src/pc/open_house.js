(function(){

    require.config({
        paths: {
            jquery: 'lib/jquery.min',
            'jquery.modal': 'lib/jquery.modal.min',
            tools: 'lib/modal.tools'
        },
        shim: {
          'jquery.modal': ['jquery']
        }
    });
    require(['jquery',"tools"], function($,tool) {
        var reg = /^1\d{10}$/;
        var isphone = function(date){
            if(date.ret_code == 10000){
                $(".mesg,.dialog").show();
            }else{
                if(date.message.name){
                    $(".lg_name").text(date.message.name[0]);
                }
                if(date.message.address){
                    $(".lg_address").text(date.message.address[0]);
                }
                if(date.message.phone){
                    $(".lg_phone").text(date.message.phone[0]);
                }
            }
        };
        var ajaxFn = function(url,option){
            $.ajax({
               type : "post",
               url : url,
               data : option,
               async : false,
               success : function(date){
                   isphone(date);
               },
               error : function(){
                    alert("网络出错，稍后再试");
               }
           })
        };
        var Event = function(){
            var phone = $("#phone").val(),
                name = $("#username").val(),
                address = $("#address").val();
            var opt = {"phone": phone, "name": name, "address": address};
            if(!reg.test(phone)){
                $(".lg_phone").text("*手机号输入错误");
            }else{
                ajaxFn("/api/activity_user_info/upload/",opt);
            }
        };

        $("#login_btn").on("click",Event);
        $("#lg_uls").on("keyup","input",function(){
            $(this).next().text("");
        })
        $("#dia_btn").on("click",function(){
            $(".mesg,.dialog").hide();
            location.reload();
        })
    })
}).call(this);