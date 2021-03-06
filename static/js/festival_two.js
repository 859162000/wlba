var org = (function () {
    document.body.addEventListener('touchstart', function () {
    }); //ios 触发active渲染
    var lib = {
        scriptName: 'mobile.js',
        _ajax: function (options) {
            $.ajax({
                url: options.url,
                type: options.type,
                data: options.data,
                dataType: options.dataType,
                async: options.async,
                beforeSend: function (xhr, settings) {
                    options.beforeSend && options.beforeSend(xhr);
                    //django配置post请求
                    if (!lib._csrfSafeMethod(settings.type) && lib._sameOrigin(settings.url)) {
                        xhr.setRequestHeader('X-CSRFToken', lib._getCookie('csrftoken'));
                    }
                },
                success: function (data) {
                    options.success && options.success(data);
                },
                error: function (xhr) {
                    options.error && options.error(xhr);
                },
                complete: function () {
                    options.complete && options.complete();
                }
            });
        },
        _calculate: function (dom, callback) {
            var calculate = function (amount, rate, period, pay_method) {
                var divisor, rate_pow, result, term_amount;
                if (/等额本息/ig.test(pay_method)) {
                    rate_pow = Math.pow(1 + rate, period);
                    divisor = rate_pow - 1;
                    term_amount = amount * (rate * rate_pow) / divisor;
                    result = term_amount * period - amount;
                } else if (/日计息/ig.test(pay_method)) {
                    result = amount * rate * period / 360;
                } else {
                    result = amount * rate * period / 12;
                }
                return Math.floor(result * 100) / 100;
            };

            dom.on('input', function () {
                _inputCallback();
            });

            function _inputCallback() {
                var earning, earning_element, earning_elements, fee_earning;
                var target = $('input[data-role=p2p-calculator]'),
                    existing = parseFloat(target.attr('data-existing')),
                    period = target.attr('data-period'),
                    rate = target.attr('data-rate') / 100,
                    pay_method = target.attr('data-paymethod');
                activity_rate = target.attr('activity-rate') / 100;
                activity_jiaxi = target.attr('activity-jiaxi') / 100;
                amount = parseFloat(target.val()) || 0;

                if (amount > target.attr('data-max')) {
                    amount = target.attr('data-max');
                    target.val(amount);
                }
                activity_rate += activity_jiaxi;
                amount = parseFloat(existing) + parseFloat(amount);
                earning = calculate(amount, rate, period, pay_method);
                fee_earning = calculate(amount, activity_rate, period, pay_method);

                if (earning < 0) {
                    earning = 0;
                }
                earning_elements = (target.attr('data-target')).split(',');

                for (var i = 0; i < earning_elements.length; i++) {
                    earning_element = earning_elements[i];
                    if (earning) {
                        fee_earning = fee_earning ? fee_earning : 0;
                        earning += fee_earning;
                        $(earning_element).text(earning.toFixed(2));
                    } else {
                        $(earning_element).text("0.00");
                    }
                }
                callback && callback();
            }
        },
        _getQueryStringByName: function (name) {
            var result = location.search.match(new RegExp('[\?\&]' + name + '=([^\&]+)', 'i'));
            if (result == null || result.length < 1) {
                return '';
            }
            return result[1];
        },
        _getCookie: function (name) {
            var cookie, cookieValue, cookies, i;
            cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                cookies = document.cookie.split(';');
                i = 0;
                while (i < cookies.length) {
                    cookie = $.trim(cookies[i]);
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                    i++;
                }
            }
            return cookieValue;
        },
        _csrfSafeMethod: function (method) {
            return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
        },
        _sameOrigin: function (url) {
            var host, origin, protocol, sr_origin;
            host = document.location.host;
            protocol = document.location.protocol;
            sr_origin = '//' + host;
            origin = protocol + sr_origin;
            return (url === origin || url.slice(0, origin.length + 1) === origin + '/') || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + '/') || !(/^(\/\/|http:|https:).*/.test(url));
        },
        _setShareData: function (ops, suFn, canFn) {
            var setData = {};
            if (typeof ops == 'object') {
                for (var p in ops) {
                    setData[p] = ops[p];
                }
            }
            typeof suFn == 'function' && suFn != 'undefined' ? setData.success = suFn : '';
            typeof canFn == 'function' && canFn != 'undefined' ? setData.cancel = canFn : '';
            return setData
        },
        /*
         * 分享到微信朋友
         */
        _onMenuShareAppMessage: function (ops, suFn, canFn) {
            wx.onMenuShareAppMessage(lib._setShareData(ops, suFn, canFn));
        },
        /*
         * 分享到微信朋友圈
         */
        _onMenuShareTimeline: function (ops, suFn, canFn) {
            wx.onMenuShareTimeline(lib._setShareData(ops, suFn, canFn));
        },
        _onMenuShareQQ: function () {
            wx.onMenuShareQQ(lib._setShareData(ops, suFn, canFn));
        }
    }
    return {
        scriptName: lib.scriptName,
        ajax: lib._ajax,
        calculate: lib._calculate,
        getQueryStringByName: lib._getQueryStringByName,
        getCookie: lib._getCookie,
        csrfSafeMethod: lib._csrfSafeMethod,
        sameOrigin: lib._sameOrigin,
        onMenuShareAppMessage: lib._onMenuShareAppMessage,
        onMenuShareTimeline: lib._onMenuShareTimeline,
        onMenuShareQQ: lib._onMenuShareQQ,
    }
})();

var utils = {
    getQueryString: function(name){
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
        var r = window.location.search.substr(1).match(reg);
        if (r != null) return unescape(r[2]); return null;
    },
    hasQueryString: function(name){
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
        var r = window.location.search.substr(1).match(reg);
        if (r != null){
            return true;
        }else{
            return false;
        }
    },
    checkMobile: function(str){
        var re = /^1\d{10}$/;
        if (re.test(str)) {
            return true;
        } else {
            return false;
        }
    },
    completeChar: function(str,num){
        str = String(parseInt(str));
        var l = str.length;
        if(l < num){
            var c = num - l;
            for(var i = 0;i < c; i++){
                str = '0' + str;
            }
        }
        return str;
    }
};

var myApp ={
    //totalImages: g_resources.length,
    //loadedImages: 0,
    music: document.getElementById("audio_bg"),
    ajaxSwitch01: true,
    ajaxSwitch011: true,
    foodOne: 0,
    foodTwo: 0,
    remLayout: {
        switch: false,
        psdWidth: 640,
        psdHeight: 1008,
        fontSizeK: 26,
        resizeEvt: 'orientationchange' in window ? 'orientationchange' : 'resize'
    },
    windowWidth: $(window).width(),
    windowHeight: $(window).height(),
    isOnlyExternal: true,
    pages: $('.swiper-slide').size(),
    slideChangeStart: function(swiper){
        //console.log(swiper.activeIndex);
    },
    slideChangeEnd: function(swiper) {
        //console.log(swiper.activeIndex);
        //this.initArrow(swiper.activeIndex);
        //this.initPagesAnimation(swiper.activeIndex,this.pages);
        //this.initSwipeLock(swiper.activeIndex);
        switch(swiper.activeIndex)
        {
            case 0:
                break;
            case 1:
                this.initPage02();
                break;
            case 2:
                break;
            case 3:
                break;
            case 4:
                break;
            case 5:
                break;
            default:
        }
    },
    initSwipeLock: function(index){
        if(index == 3){
            myApp.mySwiper.lockSwipeToNext();
        }else if(index == 4 || index == 5){
            //console.log('ss');
            //myApp.mySwiper.lockSwipes()
            //myApp.mySwiper.lockSwipeToPrev();
        }else{
            myApp.mySwiper.unlockSwipeToNext();
        }
    },
    initArrow: function(index){
        if(index == 3 || index == 4 || index == 5){
            $('#arrow').hide();
        }else{
            $('#arrow').show();
        }
    },
    initPagesAnimation: function(index,pages){
        function handelPage(index){
            var str1 = '#panel-page0';
            var str2 = '.animation';
            for(var i = 0; i < pages; i++){
                if(i == index - 1){
                    $(str1+index+' '+str2).addClass('active');
                }else{
                    $(str1+(i + 1)+' '+str2).removeClass('active');
                }
            }
        }
        handelPage(index + 1);
    },
    audioPlay: function(){
        this.music.play();
    },
    audioPause: function(){
        this.music.pause();
    },
    audioMuted: function(){
        this.music.muted = true;
    },
    audioCancelMuted: function(){
        this.music.muted = false;
    },
    initPage01 : function(){
        setTimeout(function(){
            $('#panel-page01 .table .guideText').fadeOut(1000);
            $('#panel-page01 .table .foods').fadeIn(1000);
            $('#panel-page01 .layer03').fadeIn(1000);
        },1000);
    },
    initPage02 : function(){
        setTimeout(function(){
            $('#panel-page02 .table .guideText').fadeOut(1000);
            $('#panel-page02 .table .foods').fadeIn(1000);
            $('#panel-page02 .prompt').fadeIn(1000,function(){
                $(this).addClass('active');
            });
        },1000);
    },
    handelResult01: function(obj){
         var dom = $("#go_next");
        if(obj.ret_code == 0){
            if(!obj.is_wanglibao){
                dom.attr("href","/weixin/regist/");
            }else{
                dom.attr("href","/weixin/login/");
            }
            setTimeout(function(){
                myApp.ajaxSwitch01 = true;
                myApp.ajaxSwitch011 = true;
                myApp.mySwiper.slideNext(true,1000);
            },1000);
        }else{
            myApp.ajaxSwitch01 = true;
            myApp.ajaxSwitch011 = true;
            alert(obj.message);
        }
    }
};

$(function(){


    //console.log(myApp.pages);

    //init html font-size for remLayout
    //if(myApp.remLayout.switch){
    //    console.log(myApp.windowWidth +':::'+ myApp.windowHeight);
    //    $('html').css({
    //        'font-size': myApp.windowWidth * myApp.remLayout.fontSizeK / myApp.remLayout.psdWidth
    //    });
    //
    //    $(window).on(myApp.remLayout.resizeEvt,function(){
    //        myApp.windowWidth = $(window).width();
    //        myApp.windowHeight = $(window).height();
    //        console.log(myApp.windowWidth +':::'+ myApp.windowHeight);
    //        $('html').css({
    //            'font-size': myApp.windowWidth * myApp.remLayout.fontSizeK / myApp.remLayout.psdWidth
    //        });
    //    });
    //
    //}

    //init body
    $('body').css({
        width : myApp.windowWidth,
        height: myApp.windowHeight
    });

    //微信浏览器坑爹body禁止滑动
    $('body').on('touchmove', function(){
        return false;
    });

    //iphone6s 音乐不自动播放
    $('body').one('touchstart',function(){
        if(!$("#bg_music_img").hasClass("active") && document.getElementById("audio_bg").paused){
           myApp.audioPlay();
        }
    });
    if(typeof (WeixinJSBridge) != 'undefined') {
        WeixinJSBridge.invoke('closeWindow', {}, function (res) {
            if (res.err_msg === "ok") {
                myApp.audioPause();
            }
        });
    }

    //main pages
    myApp.mySwiper = new Swiper('.swiper-container', {
        effect: "fade",
        fade: {
            crossFade: true
        },
        initialSlide: 0,
        direction: 'vertical',
        resistanceRatio : 0,
        noSwiping : true,
        noSwipingClass : 'swiper-no-swiping',
        onlyExternal: myApp.isOnlyExternal,
        onSlideChangeEnd: function(swiper){
            myApp.slideChangeEnd(swiper);
        },
        onSlideChangeStart: function(swiper){
            myApp.slideChangeStart(swiper);
        }
    });


    //loading  图片预加载
    //jQuery.imgpreload(g_resources, {
    //        each: function() {
    //            var status = $(this).data('loaded')?'success':'error';
    //            console.log($(this).attr('src')  + ' :: '+ status );
    //
    //            myApp.loadedImages++;
    //            var fixedP = Math.round(100 / 6 );
    //            var percent = Math.round(myApp.loadedImages / myApp.totalImages * 100);
    //
    //            var i = Math.floor( percent / fixedP);
    //            var op = Math.round(percent % fixedP / fixedP * 100);
    //
    //
    //            console.log(percent  + ' ::: ' + i + ' :::  ' + op);
    //            //$('#loading .people').eq(i-1).css({
    //            //    'opacity': 1
    //            //});
    //
    //            $('#loading .people').eq(i).css({
    //                'opacity': op/100
    //            });
    //
    //
    //
    //        },
    //        all: function() {
    //            console.log('all image loaded!!');
    //            //
    //            setTimeout(function(){
    //                $('#loading').fadeOut(1000,function(){
    //                    console.log('page01 start');
    //                })
    //            },2000);
    //            //$('#loading').fadeOut(1000,function(){
    //            //    console.log('page01 start');
    //            //})
    //        }
    //    });

    //自定义动画
    $.Velocity.RegisterUI('shanwei.fontIn',{
        defaultDuration: 300,
        calls: [
            [{opacity: [1,0]}]
        ]
    });
    var mainDelay = 100;
    var delay = 200;
    var duration = 200;
    var  seqLoading = [{
        elements: $('#loading .people').eq(0),
        properties: 'shanwei.fontIn',
        options: {delay: mainDelay, duration: duration}
    },{
        elements: $('#loading .people').eq(1),
        properties: 'shanwei.fontIn',
        options: {delay: delay, duration: duration}
    },{
        elements: $('#loading .people').eq(2),
        properties: 'shanwei.fontIn',
        options: {delay: delay, duration: duration}
    },{
        elements: $('#loading .people').eq(3),
        properties: 'shanwei.fontIn',
        options: {delay: delay, duration: duration}
    },{
        elements: $('#loading .people').eq(4),
        properties: 'shanwei.fontIn',
        options: {delay: delay, duration: duration}
    },{
        elements: $('#loading .people').eq(5),
        properties: 'shanwei.fontIn',
        options: {
            delay: delay,
            duration: duration,
            complete: function(){
                $('#loading').fadeOut(1000,function(){
                    myApp.initPage01();
                })
            }
        }
    }
    ];
    $.Velocity.RunSequence(seqLoading);


    //panel-page01
    var foodIsMoving = true;
    var posArray = ['pos-one','pos-two','pos-three','pos-four','pos-five','pos-six'];
    var activeArray = ['active01','active02','active03','active04','active05','active06'];
    $('#panel-page01 .foods .food').on('webkitAnimationEnd', function(){
        var p = parseInt($(this).attr('data-p')) - 1;
        $(this).removeClass(posArray[p]);
        $(this).addClass(posArray[(p+1)%6]);
        $(this).removeClass(activeArray[p]);

        $(this).attr({
            'data-p': (p+1)%6 +1
        });

        //确保只执行一次
        if(p == 0){
            foodIsMoving = false;
            $('#panel-page01 .myFoodBtn01').show();
            $('#panel-page01 .myFoodBtn02').hide();
        }

    });
    function startDisk(){
        $('#panel-page01 .foods .food').each(function(){
            var p = parseInt($(this).attr('data-p')) - 1;
            $(this).addClass(activeArray[p]);
        });
        foodIsMoving = true;
        $('#panel-page01 .myFoodBtn01').hide();
        $('#panel-page01 .myFoodBtn02').show();
    }

    //菜盘旋转
    var fps = 0.2;
    var pause = false;
    var now;
    var then = Date.now();
    var interval = 1000/fps;
    var delta;
    window.requestAnimationFrame = window.requestAnimationFrame || window.mozRequestAnimationFrame || window.webkitRequestAnimationFrame || window.msRequestAnimationFrame;

    function tick() {
        if(pause){
            return;
        }
        if(window.requestAnimationFrame)
        {
            requestAnimationFrame(tick);
            now = Date.now();
            delta = now - then;
            if (delta > interval) {
                then = now - (delta % interval);
                startDisk();
            }
        }
        else
        {
            setTimeout(tick, interval);
            startDisk();
        }
    }
    tick();



    //var foodTimer = null;
    //foodTimer = setInterval(startDisk,4500);

    //var footTimer = requestAnimationFrame(startDisk);
    //startDisk();


    //我的菜
    $('#panel-page01 .myFoodBtn01').on('touchend', function(){
        if(foodIsMoving){
            //console.log('movig');
            return false;
        }else{
            //console.log('stop');
            //window.clearInterval(foodTimer);
            pause = true ;

            $(this).hide();

            $('#panel-page01 .justItBtn').show();
            $('#panel-page01 .reelectBtn').show();
            var f = parseInt($('#panel-page01 .foods .pos-one').attr('data-f')) - 1;
            $('#panel-page01 .foods .pos-one').hide();
            $('#panel-page01 .shines .shine').eq(f).show();
            $('#panel-page01 .shines').show();

        }
    });

    //重选
    $('#panel-page01 .reelectBtn').on('touchend', function(){

        $(this).hide();
        $('#panel-page01 .justItBtn').hide();
        $('#panel-page01 .myFoodBtn01').show();
        $('#panel-page01 .myFoodBtn02').hide();
        var f = parseInt($('#panel-page01 .foods .pos-one').attr('data-f')) - 1;
        $('#panel-page01 .foods .pos-one').show();
        $('#panel-page01 .shines .shine').eq(f).hide();
        $('#panel-page01 .shines').hide();

        //startDisk();
        //foodTimer = setInterval(startDisk,4500);
        pause = false ;
        tick();
    });

    //就是它
    $('#panel-page01 .justItBtn').on('touchend', function(){
        var str = $("#redPacket1-val").val(),
            dom = $('#redPacket01'),
            html = '';
        str = eval('(' + str + ')');
        var redpack = str.redpack,
            coupon = str.coupon,
            experence = str.experience;
        //console.log(coupon,coupon.length);
        for(var i=0; i<redpack.length; i++){
            html += redpack[i].amount+"元红包（单笔投资满"+ redpack[i].invest_amount +"万可用）<br />";
        }
        for(var j=0; j<coupon.length; j++){
            html += coupon[j].amount+"%加息券<br />";
        }
        for(var m=0; m<experence.length; m++){
            if(m == (experence.length-1)){
                html += experence[m].amount+"元体验金";
            }else{
                html += experence[m].amount+"元体验金<br />";
            }
        }
        dom.find("#redPacket-cont").html(html);
        dom.show();
    });

    //红包收下 继续点菜
    $('.redPacket .orderBtn').on('touchend', function(){
        myApp.mySwiper.slideNext(true,1000)
    });

    //panel-page02

    //点击菜盘弹窗
    $('#panel-page02 .foods .food').on('touchend', function(){
        var f = $(this).index();
        var page2 = $('#panel-page02');
        var str = $("#redPacket2-val").val(),
            html = '';
        str = eval('(' + str + ')');
        //console.log(str);
        html = '<p class="big-tit">拿到'+ str['amount'] +'元红包啦！</p><p>单笔投资满'+ parseInt(str['invest_amount'])/10000 +'万可用</p>';
        page2.find('.results .result').eq(f).show().find("div.content").html(html);
        page2.find('.layer03').show();
    });

    //手机输入框切换颜色
    $('#panel-page02 #phoneNumber').on({
        'focus':function(){
            if($(this).val()=='输入手机号 领取所有红包'){
                $(this).val('');
                $(this).css({
                    'color': '#fc8910'
                });
            }
        },
        'blur':function(){
            if($(this).val()==''){
                $(this).css({
                    'color': '#cccccc'
                });
                $(this).val('输入手机号 领取所有红包');
            }
        }
    });

    //领取 AJAX 手机验证
    $('#panel-page02 .receiveBtn').on('touchend', function(){
        //alert(myApp.ajaxSwitch01);
        if(myApp.ajaxSwitch01){
            var data = {
                'phone' : $('#phoneNumber').val()
            };

            if(data.phone == '' || data.phone == '输入手机号 领取所有红包'){
                alert('请输入您的手机号码哦！');
                return false;
            }
            if(utils.checkMobile(data.phone) == false){
                alert('请输入正确的手机号码哦!');
                return false;
            }
            myApp.ajaxSwitch01 = false;
            myApp.ajaxSwitch011 = false;
            org.ajax({
                type: "POST",
                url: "/api/lantern/fetch_reward/",
                data: data,
                dataType: "json",
                success: function(data){
                    //console.log(data);
                    myApp.handelResult01(data);
                },
                error: function(e){
                    myApp.ajaxSwitch01 = true;
                    myApp.ajaxSwitch011 = true;
                    //alert($.parseJSON(e));
                    alert('服务器连接超时，请查看您的网络！');
                }
            });
        }else{
            alert('正在提交信息哦！');
        }

    });


    //debug
    //$('#panel-page02 .results .result').on('touchend', function(){
    //    $(this).hide();
    //    $('#panel-page02 .results').hide();
    //});


    //bg_music
    $('#bg_music_img').on('touchend',function(){
        $(this).toggleClass('active');
        var oAudio =  $('#audio_bg')[0];
        //console.log( $('#audio_bg')[0].paused);
        if(oAudio.paused){
            $('#audio_bg')[0].play();
        }else{
            $('#audio_bg')[0].pause();
        }
    });

    //arrow
    //$('#arrow').on('click', function(){
    //    myApp.mySwiper.slideNext(true);
    //});

    //share
    //$('#share').on('click', function(){
    //    $(this).hide();
    //});

    function weixin_share(shareTit,fn){
        //alert(shareTit);
        var weiURL = '/weixin/api/jsapi_config/';
        var jsApiList = ['scanQRCode', 'onMenuShareAppMessage', 'onMenuShareTimeline', 'onMenuShareQQ'];
        $.ajax({
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
            var winHost = window.location.href;
            var host = $.trim($("#shareUrl").val());
			//var host = 'https://staging.wanglibao.com',
            var shareImg = 'https://www.wanglibao.com/static/imgs/mobile/weChat_logo.png',
                shareLink = host,
                shareMainTit = shareTit,
                shareBody = '闹元宵，吃大餐，抽红包财源滚滚来';

            //分享给微信好友
            wx.onMenuShareAppMessage({
                title: shareMainTit,
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
            wx.onMenuShareTimeline({
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
            wx.onMenuShareQQ({
                title: shareMainTit,
                desc: shareBody,
                link: shareLink,
                imgUrl: shareImg,
                success: function(){
                    //alert(1);
                    if(fn && (typeof fn == "function")){
                        //alert(3);
                        fn();
                    }
                }
            })
        })
    }
	weixin_share("猴年赚不赚，就吃元宵宴");//微信分享
});