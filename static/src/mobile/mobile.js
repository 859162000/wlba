
var org = (function(){
    var lib = {
        scriptName: 'mobile.js',
        test :function(){
            console.log('test')
        }
    }
    return {
        scriptName : lib.scriptName
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
                url: '/api/p2ps/wx',
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

var detail = (function(){
    var lib ={
        weiURL: '/weixin/jsapi_config.json',
        init :function(){
            lib._tab();
            lib._animate();
            lib._share()
        },
        _animate:function(){
            var $progress = $('.progress-percent');
            $(function(){
                setTimeout(function(){
                    var percent = parseFloat($progress.attr('data-percent'));
                    percent == 100 ? $progress.css("height",'110%') : $progress.css("height", percent + '%');
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
                  var data = data.result;
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
                console.log(11)
            })

        }
    }
    return {
        init : lib.init
    }
})()

~(function(org){
    $.each($("script"), function(index, item){
      if($(this).attr("src").indexOf(org.scriptName) > 0){
        if($(this).attr("data-init") && window[$(this).attr("data-init")]){
            window[$(this).attr("data-init")].init()
        }
      }
    })
})(org)
