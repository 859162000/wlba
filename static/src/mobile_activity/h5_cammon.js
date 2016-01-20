(function(){
    var jqDom = $("div.mammon-jq");
    var page2 = $("div.mammon-page2");
    function shareBack(){
        $("div.mammon-page1, div.mammon-jq, div.mammon-share").hide();
        page2.show();
    }
    function getVal(){
        var val = [
            {"qVal": "中签","title":"鸿运","detail":"福致心灵，鸿喜云集，新年开运"},
            {"qVal": "中签","title":"荣归","detail":"学富五车题雁塔<br />衣锦还乡会有时"},
            {"qVal": "上签","title":"利是","detail":"得鸿运 利仕途 能旺夫"},
            {"qVal": "上签","title":"致祥","detail":"竹报三多 和睦融洽 可致吉祥"},
            {"qVal": "上签","title":"吉祥","detail":"梅花数点 泽如时雨 吉人天相"},
            {"qVal": "上上签 ","title":"福聚","detail":"日转千阶 洞房花烛<br />久旱逢雨 他乡故知"},
        ];
        var inx = parseInt(Math.random()*7);
        //console.log(inx,val[inx].qVal,val[inx].title, val[inx].detail.replace("<br />"," "));

        jqDom.find("div.top").text(val[inx].qVal);//签
        jqDom.find("div.bottom").text(val[inx].title);

        page2.find("div.big-tit").text(val[inx].title);
        page2.find("div.qian-cont").html(val[inx].detail);

        weixin_share(val[inx].detail.replace("<br />"," "),shareBack);//微信分享
    }
    $("div.shake-box").click(function(){
        var self = $(this);
        self.find("p.shake-tit").hide();
        self.parents("div.mammon-yb").addClass("circle-box");
        showJp(self.find("img"));
    });
    function showJp(self){//显示 签
        setTimeout(function(){
            self.removeClass("shake");
            $("div.mammon-jq").css("display","-webkit-box");
        },6000);
    }
    function checkTel(val){
        var isRight = false,
            re = new RegExp(/^[1][0-9]{10}$/);
        re.test($.trim(val)) ? isRight = true : isRight = false;
        return isRight;
    }
    function weixin_share(shareTit,fn){
        alert(shareTit);
        var weiURL = '/weixin/api/jsapi_config/';
        var jsApiList = ['scanQRCode', 'onMenuShareAppMessage', 'onMenuShareTimeline', 'onMenuShareQQ'];
        org.ajax({
            type: 'GET',
            url: weiURL,
            dataType: 'json',
            success: function (data) {
                //请求成功，通过config注入配置信息,
                wx.config({
                    debug: false,
                    appId: data.appId,
                    timestamp: data.timestamp,
                    nonceStr: data.nonceStr,
                    signature: data.signature,
                    jsApiList: jsApiList
                });
            }
        });
        wx.ready(function () {
            var host = 'https://staging.wanglibao.com',
                shareImg = host + '/static/imgs/mobile_activity/mammon/cs_img.png',
                shareLink = host + '/activity/weixin_mammon/',
                shareMainTit = shareTit ? ('《财神说：'+shareTit +'》') : '《财神说：接财神、测财运、领开运红包》',
                shareBody = shareTit;
            //分享给微信好友
            org.onMenuShareAppMessage({
                title: "《财神说：接财神、测财运、领开运红包》",
                desc: shareBody,
                link: shareLink,
                imgUrl: shareImg,
                success: function(){
                    //alert("分享成功");
                    if(fn && (typeof fn == "function")){
                        fn();
                    }
                }
            });
            //分享给微信朋友圈
            org.onMenuShareTimeline({
                title: shareMainTit,
                link: shareLink,
                imgUrl: shareImg,
                success: function(){
                    if(fn && (typeof fn == "function")){
                        fn();
                    }
                }
            });
            //分享给QQ
            org.onMenuShareQQ({
                title: shareMainTit,
                desc: shareBody,
                link: shareLink,
                imgUrl: shareImg,
                success: function(){
                    if(fn && (typeof fn == "function")){
                        fn();
                    }
                }
            })
        })
    }

    getVal();

    //点击解签
    $(".js-btn").click(function(){
        $(this).parents(".mammon-jq").hide();
        $("div.mammon-share").css("display","-webkit-box");
    });
    //关闭弹出层
    $(".js-close").click(function(){
        $(this).parents(".alt-box").hide();
    });

    //手机号 检测是否是新用户
    $(".js-checkUser").click(function(){
        var self = $(this);
        var tel = self.siblings(".tel-inp").val();
        var tp = self.parents("div.mammon-page2");
        if(!checkTel(tel)){
            $("div.mammon-error").css("display","-webkit-box").find(".share-txt").html("请正确填写手机号");
            return false;
        }
        $.ajax({
            type: "GET",
            url: '/api/user_exists/'+tel,
            dataType: 'json',
            success: function(data){
                if(data.existing){
                    tp.hide();
                    tp.siblings("div.mammon-page3").show();
                }else{
                    tp.hide();
                    tp.siblings("div.mammon-page4").show().find("#page4-tel").text(tel);
                }
            }
        });
    });
})();
