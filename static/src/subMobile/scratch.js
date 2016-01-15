;(function(){
    window.onload = function () {
        onLoadClass();
        var lotteryContainer = document.getElementById("lotteryContainer");
        var lottery = new Lottery('lotteryContainer', '/static/imgs/sub_weixin/activity/ggl_area.jpg', 'image', lotteryContainer.width || lotteryContainer.offsetWidth, lotteryContainer.height || lotteryContainer.offsetHeight, drawPercent, startTouch);
        lottery.init(getRandomStr(), 'text');
        var freshBtn = $('#freshBtn');
        freshBtn.click(function() {
            //drawPercentNode.innerHTML = '0%';
            document.getElementById("lotteryContainer").style.display = "block";
            lottery.init(getRandomStr(), 'text');
        });

        function drawPercent(percent) {
            if(percent > 60){
                document.getElementById("lotteryContainer").style.display = "none";
            }
        }
        var errorArr = ['专家建议，刮奖的动作不要太矜持~','佛说：前世的500次回眸才换得今生的一次中奖，淡定~','老夫夜观星象，晚上中奖几率更高哦~','大奖何时有?把酒问青天~','你离中奖只有一根头发的距离~','据说心灵纯洁的人中奖几率更高~','刮前吼三吼，大奖跟我走~'];
        var txtDom = $("#award-txt");
        function closePage(){ //没有抽奖机会或不符合
            freshBtn.text("确定").unbind("click").on("click",function(){
                if(typeof (WeixinJSBridge) != 'undefined'){
                    WeixinJSBridge.call('closeWindow');
                }else{
                    window.close();
                }
            });
        }
        function startTouch(){
            var url = window.location.search;
            var orderId = url.substring(url.lastIndexOf('=')+1, url.length);
            org.ajax({
                type: 'post',
                url: '/api/weixin/guaguaka/',
                data: {"order_id": orderId},
                dataType: 'json',
                success: function(data){
                    console.log(data);

                    if(data.code === 0){
                        txtDom.html('人品大爆发，'+ data.amount +'%加息券已经悄悄飞到了您的账户中~');
                    }else if(data.code === 1){
                        var random = parseInt(Math.random()*errorArr.length);
                        var str = errorArr[random];
                        txtDom.html(str);
                        errorArr.splice(random,1);
                    }else if(data.code === 1002){
                        txtDom.html('您的人品已经用完，继续投资、提现再来碰运气吧~');
                        closePage();
                    }else{
                        txtDom.html('您不符合刮奖条件，仔细阅读活动规则哦~');
                        closePage();
                    }
                    $("#chance-num").text(data.lefts || 0);
                },
                error: function(){
                    //window.location.href="/weixin/jump_page/?message=出错了，请稍候再试";
                }
            });
        }
    };

    function getRandomStr() {
        $("#award-txt").html('');
        return '刮刮乐';
    }

    $(".scratch-rule").on("click", function(){
        $("#scratch-alt").css("display", "-webkit-box");
    });
    $(".close-alt").on("click", function(){
        $(this).parents("#scratch-alt").hide();
    });
    org.detail.share({
        'shareLink': 'https://staging.wanglibao.com/weixin/activity_ggl/',
        'shareMainTit':'刮刮乐翻天 红包滚滚来',
        'shareBody':'刮刮乐翻天 红包滚滚来'
    });
})();