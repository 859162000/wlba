//请求票数接口
$('.damai-buttonold').click(function () {
    redpack();
})

function redpack() {
    org.ajax({
        url: '/api/rock/finance/old_user/',
        type: "POST",
        data: {}
    }).done(function (damai) {
        console.log(damai);
        if (damai['ret_code'] == 0) {
           $('.tishiyu').text('您已获得门票');
        } else if (damai['ret_code'] == 1006) {
            $('.tishiyu').text('您已领过门票');
        } else if (damai['ret_code'] == 1005) {
            $('.tishiyu').text('很抱歉，奖品发没了');
        } else if (damai['ret_code'] == 1004) {
            $('.tishiyu').text('很抱歉，没有在预定的时间内购标');
        } else if (damai['ret_code'] == 1003) {
            $('.tishiyu').text('很抱歉，票已经发完了');
        } else if (damai['ret_code'] == 1001) {
            $('.tishiyu').text('很抱歉，您投资没有满5000元');
            console.log('没有投资满5000');
        }


    });
};