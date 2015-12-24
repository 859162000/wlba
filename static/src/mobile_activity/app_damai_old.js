//请求票数接口
$('.damai-buttonold').click(function () {
    redpack();
})

function redpack() {
    org.ajax({
        url: '/api/rock/finance/old_user/',
        type: "POST",
        data: {},
        success: function (damai) {
            if (damai['ret_code'] == 0) {
                $('.tishiyu').text('恭喜！您已获得网利宝摇滚之夜门票');
            } else if (damai['ret_code'] == 1006) {
                $('.tishiyu').text('您已领过网利宝摇滚之夜门票');
            } else if (damai['ret_code'] == 1005) {
                $('.tishiyu').text('很抱歉，门票已经发完了');
            } else if (damai['ret_code'] == 1004) {
                $('.tishiyu').text('很抱歉，没有在预定的时间内购标');
            } else if (damai['ret_code'] == 1003) {
                $('.tishiyu').text('很抱歉，门票已经发完了');
            } else if (damai['ret_code'] == 1001) {
                $('.tishiyu').text('很抱歉，您投资没有满1000元');
            }
        }


    })
};