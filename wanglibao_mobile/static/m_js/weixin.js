(function () {

    $('.wei_kehuduan>a').on('click', function () {
        $('.wei_kehuduan').hide();
    });

    log();

})();
function log(){
    $('.judge').on('click', function () {
        if ($(".ipon").val() == "") {
            alert("手机号码不能为空！");
            $(".ipon").focus();
            return false;
        } else if (!$(".ipon").val().match(/^1[3|4|5|8|9][0-9]\d{4,8}$/)) {
            alert("手机号码格式不正确！");
            $(".ipon").focus();
            return false;
        } else {
             var userName = $.trim($(".ipon").val());
            $.ajax({
                type: "get",
                url: "/api/user_exists/" + userName,
                data:{

                },
                dataType: "json",
                success: function (result) {
                    console.log(result['existing']);
                    var number_a=result['existing'];
                   if(number_a===true){
                       window.location.href = "/mobile/weixin_inputt/";
                   }else{
                        window.location.href = "/mobile/weixin_registered/";
                   }
                }
            });
        }
    });
}





