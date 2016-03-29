(function(org){
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
            org.ajax({
               type : "post",
               url : url,
               data : option,
               async : false,
               success : function(date){
                   console.log(date)
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
            if(phone == ""){
                $(".lg_phone").text("*请输入手机号");
            }else if(!reg.test(phone)){
                $(".lg_phone").text("*手机号输入错误");
            }else if(strlen(name)>20){
                $(".lg_name").text("*姓名输入错误");
            }else if(strlen(address)>20){
                $(".lg_address").text("*地址输入错误");
            }else{
                ajaxFn("/api/activity_user_info/upload/",opt);
            }
        };
        function strlen(str){
            var len = 0;
            for(var i=0; i<str.length; i++){
                var c = str.charCodeAt(i);
                if ((c >= 0x0001 && c <= 0x007e) || (0xff60<=c && c<=0xff9f)) {
                   len++;
                 }
                 else {
                  len+=2;
                 }
            }
            return len;
        }

        $("#login_btn").on("click",Event);
        $("#lg_uls").on("input","input",function(){
            $(this).next().text("");
        })
        $("#dia_btn").on("click",function(){
            $(".mesg,.dialog").hide();
            location.reload();
        })
})(org)