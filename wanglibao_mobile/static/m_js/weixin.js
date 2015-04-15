(function () {

    $('.wei_kehuduan>a').on('click', function () {
        $('.wei_kehuduan').hide();
    });

    $('.judge').on('click', function () {
        if ($(".ipon").val() == "") {
            alert("手机号码不能为空！");
            $(".ipon").focus();
            return false;
        } else if (!$(".ipon").val().match(/^(((13[0-9]{1})|159|153)+\d{8})$/)) {
            alert("手机号码格式不正确！");
            $(".ipon").focus();
            return false;
        } else {
             var userName = $.trim($(".ipon").val());
            $.ajax({
                type: "get",
                url: "user_exists/userName",
                data:{},
                dataType: "number",
                success: function (result) {

                }
            });
        }
    });


})();




