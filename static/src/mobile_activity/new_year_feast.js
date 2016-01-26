org.ui = (function(){
    var lib = {
        _alert: function(txt, callback,difference){
            var alertFram = '';
            if(document.getElementById("alert-cont")){
                document.getElementById("alert-cont").innerHTML = '';
                document.getElementById("popubMask").style.display = "block";
                document.getElementById("alert-cont").style.display = "block";
                alertFram = document.getElementById("alert-cont");
                shield = document.getElementById("popubMask");
            }else{
                var shield = document.createElement("DIV");
                shield.id = "popubMask";
                shield.style.cssText="position:fixed;bottom:0;top:0;width:100%; background:rgba(0,0,0,0.8); z-index:1000000;height:100%";
                alertFram = document.createElement("DIV");
                alertFram.id="alert-cont";
            }
            if(difference == 2){
                var strHtml = "<div id='packets' class='packets alertT30 clearfix'><div class='packets-bg'><div class='packets-content'>"+ txt +"</div></div>"
                            +"<p class='yellow-fonts'>领取成功！</p><p class='yellow-fonts'>进去“我的账户”－－“理财券”及“体验金专区”查看</p>"
                            +"<div class='close-b close-min'></div></div>";
            }else if(difference == 3){
                var strHtml ="<div id='packets' class='packets clearfix'><div class='alert-style'></div><div class='alert-bg'>"+ txt +"</div>"
                    +"<div class='close-b close-max'></div></div>"
            }
            alertFram.innerHTML = strHtml;
            document.body.appendChild(alertFram);
            document.body.appendChild(shield);

            $('.close-b').on('click',function(){
                alertFram.style.display = "none";
                shield.style.display = "none";
                callback && callback();
            })
            document.body.onselectstart = function(){return false;};
        }
    }

    return {
        alert : lib._alert
    }
})();
org.feast = (function (org) {
    var lib = {
        arrow : $('.arrow'),
        init: function () {
            lib._potAward();
            lib._receiveFun();
        },
        /*开锅箭头样式*/
        _arrowStyle: function(index,tag){
           var potIndex1 = $('.pot-s[index="'+ index +'"]'),
                top = potIndex1.position().top,
                left = potIndex1.position().left,
                width = potIndex1.width();
            tag == 'default' ? lib.arrow.show(): '';
            var arrowHeight = lib.arrow.height(),
                arrowWidth = lib.arrow.width();
            lib.arrow.css({
                top : top - (arrowHeight*0.8),
                left : left + (width/2) - (arrowWidth/2)
            })
        },
        /*开锅赢福利*/
        _potAward:function(){
             $('.pot-s').click(function(){
                 var index = $(this).attr('index');
                 if($('#authenticated').val() == 'True'){
                    if(!$('.pot-s').hasClass('selectEd')){
                         org.ajax({
                            url: '/api/wlb_reward/qm_banque/',
                            type: 'post',
                            data: {},
                            success: function (data) {
                                if(data.ret_code == 0){
                                    var i = 1,j = 0,txt='';
                                    $.each(data.redpack_txts,function(i,o){
                                       txt+='<p>'+ o +'</p>'
                                    })
                                    var timer = setInterval(function(){
                                        i == 4 ? i = 0 : i = i;
                                        if((j>3) && (i == (index - 1))){
                                            clearInterval(timer);
                                            setTimeout(function(){
                                                org.ui.alert(txt, '', '2')
                                                $('.pot-s').removeClass('selectEd')
                                            },500)
                                        }
                                        lib._arrowStyle(i+1)
                                        i++,j++;
                                    },500)
                                    $('.pot-s').addClass('selectEd')
                                }else{
                                    org.ui.alert('<p class="error-s">'+data.message+'</p>', '', '3')
                                }
                            }
                         })
                     }
                 }else{
                     window.location.href = '/weixin/login/?next=/weixin_activity/qm_banquet/';
                 }
             })
        },
        _lookMoreInfoFun: function(){
            $('#lookMoreInfo').click(function(){
                var obj = $('.moreInfo'),
                    curHeight = obj.height(),
                    autoHeight = obj.css('height', 'auto').height();
                if (!obj.hasClass('down')){
                  obj.height(curHeight).animate({height: autoHeight},500,function(){
                    obj.addClass('down')
                  });
                }else{
                  obj.height(curHeight).animate({height: 0},500,function(){
                    obj.removeClass('down')
                  });
                }
            })
            $('#projectList').click(function(){
                window.location.href = '/weixin/list/';
            })
        },
        _receiveFun: function(){
            $('.packets-btn a').click(function(){
                if ($('#authenticated').val() == 'True') {
                    var id = $(this).attr('data-id');
                    org.ajax({
                        url: '/api/wlb_reward/hm_banque/',
                        type: 'post',
                        data: {
                            redpack_id : id
                        },
                        success: function (data) {
                            if(data.ret_code == 0){
                                var txt = '<p class="title-s">领取成功！</p><p class="pop-fonts">进去“我的账户”－－“理财卷”及“体验金专区”查看</p>';
                                org.ui.alert(txt, '', '3')
                            }else{
                                org.ui.alert('<p class="error-s">'+data.message+'</p>', '', '3')
                            }
                        }
                    })
                } else {
                    window.location.href = '/weixin/login/?next=/weixin_activity/qm_banquet/';
                }
            })
        }
    }
    return {
        init: lib.init,
        arrowStyle: lib._arrowStyle,
        lookMoreInfoFun: lib._lookMoreInfoFun
    }
})(org);
org.feast.arrowStyle(1,'default');
org.feast.lookMoreInfoFun();
wlb.ready({
    app: function (mixins) {
        function connect(data) {
            org.ajax({
                url: '/accounts/token/login/ajax/',
                type: 'post',
                data: {
                    token: data.tk,
                    secret_key: data.secretToken,
                    ts: data.ts
                },
                success: function (data) {
                    var url = location.href;
                    var times = url.split("?");
                    if(times[1] != 1){
                        url += "?1";
                        self.location.replace(url);
                    }
                    org.feast.init()
                }
            })
        }

        mixins.sendUserInfo(function (data) {
            $('#projectList').on('click',function(){
                mixins.jumpToManageMoney();
            })
            if (data.ph == '') {
                $('.pot-s,.packets-btn a').on('click',function(){
                    mixins.loginApp({refresh: 1, url: ''})
                })
            } else {
                connect(data)
            }
        })


    },
    other: function () {
        org.feast.init()
    }
})
var weChatShare = (function(org){
    var jsApiList = ['scanQRCode', 'onMenuShareAppMessage','onMenuShareTimeline','onMenuShareQQ',];
        org.ajax({
            type : 'GET',
            url : '/weixin/api/jsapi_config/',
            dataType : 'json',
            success : function(data) {
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
        wx.ready(function(){
            var host = 'https://staging.wanglibao.com/activity/new_year_feast/',
                shareImg = host + '/static/imgs/mobile/weChat_logo.png',
                shareLink = window.location.href,
                shareMainTit = '新年红包宴，每天可领一次福气大礼包。',
                shareBody = '每天一次机会，开锅领奖。红包、加息券、体验金100%必中。';
            //分享给微信好友
            org.onMenuShareAppMessage({
                title: shareMainTit,
                desc: shareBody,
                link: shareLink,
                imgUrl: shareImg
            });
            //分享给微信朋友圈
            org.onMenuShareTimeline({
                title: '新年红包宴，每天可领一次福气大礼包。',
                link : shareLink,
                imgUrl: shareImg
            })
            //分享给QQ
            org.onMenuShareQQ({
                title: shareMainTit,
                desc: shareBody,
                link : shareLink,
                imgUrl: shareImg
            })
        })
})(org);
