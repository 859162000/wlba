
var org = (function(){
    var lib = {
        scriptName: 'mobile.js',
        _setShareData:function(ops,suFn,canFn){
            var setData = {};
            if(typeof ops == 'object'){
                for(var p in ops){
                    setData[p] = ops[p];
                }
            }
            typeof suFn =='function' && suFn != 'undefined' ? setData.success = suFn : "";
            typeof canFn =='function' && canFn != 'undefined' ? setData.cancel = canFn : "";
            return setData
        },
        /*
         * 分享到微信朋友
         */
        _onMenuShareAppMessage:function(ops,suFn,canFn){
            wx.onMenuShareAppMessage(lib._setShareData(ops,suFn,canFn));
        },
        /*
         * 分享到微信朋友圈
         */
        _onMenuShareTimeline:function(ops,suFn,canFn){
            wx.onMenuShareTimeline(wShare._setShareData(ops,suFn,canFn));
        }
    }
    return {
        scriptName : lib.scriptName,
        onMenuShareAppMessage : lib._onMenuShareAppMessage,
        onMenuShareTimeline : lib._onMenuShareTimeline
    }
})()

//list
var list = (function(org){
    var lib = {
        windowHeight : $(window).height(),
        canGetPage : true, //防止多次请求
        scale : 0.7, //页面滚到百分70的时候请求
        pageSize: 10, //每次请求的个数
        page: 2, //从第二页开始
        init :function(){
            lib._scrollListen();
        },
        _scrollListen:function(){
            $(document).scroll(function(){
                if(document.body.scrollTop / (document.body.clientHeight -lib.windowHeight ) >= lib.scale){
                    lib.canGetPage && lib._getNextPage();
                }
            });
        },
        _getNextPage :function(){
            $.ajax({
                type: 'GET',
                url: '/api/p2ps/wx/',
                data: {page: lib.page, 'pagesize': lib.pageSize},
                beforeSend:function(){
                    lib.canGetPage =false
                },
                success: function(data){
                   $("#list-body").append(data.html_data);
                    lib.page++;
                    lib.canGetPage = true;
                },
                error: function(xhr, type){
                    alert('Ajax error!')
                }
            })
        }

    };
    return {
        init : lib.init
    }
})(org)

var detail = (function(org){
    var lib ={
        weiURL: '/weixin/jsapi_config.json',
        countDown: $('#countDown'),
        init :function(){
            lib._tab();
            lib._animate();
            lib._share();
            lib.countDown.length > 0 && lib._countDown(lib.countDown)
        },
        _animate:function(){
            var $progress = $('.progress-percent');
            $(function(){
                setTimeout(function(){
                    var percent = parseFloat($progress.attr('data-percent'));
                    if(percent == 100){
                        $progress.css("margin-top","-10%");
                    }else{
                        $progress.css("margin-top", (100 - percent) + '%');

                    }
                    setTimeout(function(){
                        $progress.addClass('progress-bolang')
                    },1000)
                },300)
            })
        },
        _tab:function(){
            $(".toggleTab").on('click',function(){
                $(this).siblings().toggle();
                $(this).find('span').toggleClass('icon-rotate')
            })
        },
        _share: function(){
            var jsApiList = ["scanQRCode", "onMenuShareAppMessage","onMenuShareTimeline","onMenuShareQQ",];
            $.ajax({
                type : 'GET',
                url : lib.weiURL,
                dataType : "json",
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
                //分享给微信好友
                org.onMenuShareAppMessage({
                    title: "haha",
                    desc: '没有什么啦',
                    link: "https://www.wanglibao.com",
                    imgUrl: "http://demo.open.weixin.qq.com/jssdk/images/p2166127561.jpg"},
                    function(){
                        alert("分享成功");
                    }
                );
                //分享给微信朋友圈
                org.onMenuShareTimeline({
                    title: "啦啦啦",
                    link : "https://www.wanglibao.com",
                    imgUrl: "http://demo.open.weixin.qq.com/jssdk/images/p2166127561.jpg"
                })
            })

        },
        _countDown:function(target){
            var endTimeList = target.attr("data-left").replace(/-/g,"/");
            var  TimeTo =function (dd){
                var t = new Date(dd),
                    n = parseInt(new Date().getTime()),
                    c = t - n;
                if( c <= 0 ){
                    target.text('活动已结束')
                    clearInterval(window['interval']);
                    return
                }
                var ds = 60*60*24*1000,
                    d = parseInt(c/ds),
                    h = parseInt((c-d*ds)/(3600*1000)),
                    m = parseInt((c - d*ds - h*3600*1000)/(60*1000)),
                    s = parseInt((c-d*ds-h*3600*1000-m*60*1000)/1000);
                    m < 10 ? m = "0" + m: '';
                    s < 10 ? s = "0" + s: '';
                    target.text(d+'天'+h+'小时'+m+'分'+s+'秒');
            }
            window['interval']= setInterval(function(){
                TimeTo(endTimeList);
            },1000);
        }
    }
    return {
        init : lib.init
    }
})(org)

~(function(org){
    $.each($("script"), function(index, item){
      if($(this).attr("src").indexOf(org.scriptName) > 0){
        if($(this).attr("data-init") && window[$(this).attr("data-init")]){
            window[$(this).attr("data-init")].init()
        }
      }
    })
})(org)
