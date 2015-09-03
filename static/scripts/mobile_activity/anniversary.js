/* Zepto v1.1.6 - zepto event ajax form ie - zeptojs.com/license */
(function(){
    window.alert = function(txt, callback){
        if(document.getElementById("alert-cont")){
            document.getElementById("alertTxt").innerHTML = txt;
            document.getElementById("popubMask").style.display = "block";
            document.getElementById("alert-cont").style.display = "block";
        }else{
            var shield = document.createElement("DIV");
            shield.id = "popubMask";
            shield.style.cssText="position:fixed;bottom:0;top:0;width:100%; background:rgba(0,0,0,0.5); z-index:1000000;";
            var alertFram = document.createElement("DIV");
            alertFram.id="alert-cont";
            alertFram.style.cssText="position:fixed; top:35%;left:50%; width:14rem; margin:-2.75rem 0 0 -7rem; background:#fafafa; border-radius:.3rem;z-index:1000001;";
            strHtml = "<div id='alertTxt' class='popub-txt' style='color:#333;font-size: .9rem!important;padding: 1.25rem .75rem;'>"+txt+"</div>";
            strHtml +=" <div class=\"popub-footer\" style=\"width: 100%;padding: .5rem 0;font-size: .9rem;text-align: center;color: #4391da;border-top: 1px solid #d8d8d8;border-bottom-left-radius: .25rem;border-bottom-right-radius: .25rem;\" onclick=\"doOk()\">确认</div>";
            alertFram.innerHTML = strHtml;
            document.body.appendChild(alertFram);
            document.body.appendChild(shield);
            this.doOk = function(){
                alertFram.style.display = "none";
                shield.style.display = "none";
                callback && callback();
            };
        }
        document.body.onselectstart = function(){return false;};
    };
})();
var org = (function(){
    document.body.addEventListener('touchstart', function () { }); //ios 触发active渲染
    var lib = {
        scriptName: 'anniversary.js',
        _ajax :function(options){
            $.ajax({
                url: options.url,
                type: options.type,
                data: options.data,
                dataType : options.dataType,
                beforeSend: function(xhr, settings) {
                    options.beforeSend && options.beforeSend(xhr);
                    //django配置post请求
                    if (!lib._csrfSafeMethod(settings.type) && lib._sameOrigin(settings.url)) {
                      xhr.setRequestHeader('X-CSRFToken', lib._getCookie('csrftoken'));
                    }
                },
                success:function(data){
                    options.success && options.success(data);
                },
                error: function (xhr) {
                    options.error && options.error(xhr);
                },
                complete:function(){
                    options.complete && options.complete();
                }
            });
        },
        _calculate :function(dom, callback){
            var calculate = function(amount, rate, period, pay_method) {
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
            dom.on('input', function(e) {
                var earning, earning_element, earning_elements, fee_earning, fee_element, fee_elements;
                var target = $(e.target),
                    existing = parseFloat(target.attr('data-existing')),
                    period = target.attr('data-period'),
                    rate = target.attr('data-rate')/100,
                    pay_method = target.attr('data-paymethod');
                    activity_rate = target.attr('activity-rate')/100;
                    amount = parseFloat(target.val()) || 0;

                if (amount > target.attr('data-max')) {
                    amount = target.attr('data-max');
                    target.val(amount);
                }
                amount = parseFloat(existing) + parseFloat(amount);
                earning = calculate(amount, rate, period, pay_method);
                fee_earning = calculate(amount, activity_rate, period, pay_method);

                if (earning < 0) {
                    earning = 0;
                }
                earning_elements = (target.attr('data-target')).split(',');
                fee_elements = (target.attr('fee-target')).split(',');

                for (var i = 0; i < earning_elements.length; i ++) {
                    earning_element = earning_elements[i];
                    if (earning) {
                        earning += fee_earning;
                        $(earning_element).text(earning.toFixed(2));
                    } else {
                        $(earning_element).text("0.00");
                    }
                }
                for (var j = 0; j < fee_elements.length;  j++) {
                    fee_element = fee_elements[j];
                    if (fee_earning) {
                       $(fee_element).text(fee_earning);
                    } else {
                        $(fee_element).text("0.00");
                    }
                }
                callback && callback(target);
            });
        },
        _getQueryStringByName:function(name){
            var result = location.search.match(new RegExp('[\?\&]' + name+ '=([^\&]+)','i'));
             if(result == null || result.length < 1){
                 return '';
             }
             return result[1];
        },
        _getCookie :function(name){
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
        _csrfSafeMethod :function(method){
            return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
        },
        _sameOrigin:function(url){
            var host, origin, protocol, sr_origin;
            host = document.location.host;
            protocol = document.location.protocol;
            sr_origin = '//' + host;
            origin = protocol + sr_origin;
            return (url === origin || url.slice(0, origin.length + 1) === origin + '/') || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + '/') || !(/^(\/\/|http:|https:).*/.test(url));
        },
        _setShareData:function(ops,suFn,canFn){
            var setData = {};
            if(typeof ops == 'object'){
                for(var p in ops){
                    setData[p] = ops[p];
                }
            }
            typeof suFn =='function' && suFn != 'undefined' ? setData.success = suFn : '';
            typeof canFn =='function' && canFn != 'undefined' ? setData.cancel = canFn : '';
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
            wx.onMenuShareTimeline(lib._setShareData(ops,suFn,canFn));
        },
        _onMenuShareQQ:function(){
            wx.onMenuShareQQ(lib._setShareData(ops,suFn,canFn));
        }
    }
    return {
        scriptName             : lib.scriptName,
        ajax                   : lib._ajax,
        calculate              : lib._calculate,
        getQueryStringByName   : lib._getQueryStringByName,
        getCookie              : lib._getCookie,
        csrfSafeMethod         : lib._csrfSafeMethod,
        sameOrigin             : lib._sameOrigin,
        onMenuShareAppMessage  : lib._onMenuShareAppMessage,
        onMenuShareTimeline    : lib._onMenuShareTimeline,
        onMenuShareQQ          : lib._onMenuShareQQ,
    }
})();


org.anniversary = (function(org){
    var index = 0,left = 0;
    var lib = {
        init:function(){
            lib._scrollFun();
            lib._gameFun();
            lib._aboutPageFun();
            lib._winningList();
        },
        _scrollFun:function(){
            //无线滚动
            var timer,i= 1,j=2;
            timer=setInterval(function(){
              if (-parseInt($('#users').css('top'))>=$('#users li').height()){
                $('#users li').eq(0).appendTo($('#users'));
                $('#users').css({'top':'0px'})
                i=0
              }else{
                i++
                $('#users').css({'top':-i+'px'})
              }
            },30)
        },
        _gameFun:function(){
            //转盘
            $(".rotateImg").rotate({
                bind:{
                    click:function(){
                        if(!$(".rotateImg").hasClass('rotateImgNo')) {
                            if (left > 0) {
                                org.ajax({
                                    url: '/api/celebrate/awards/',
                                    type: "POST",
                                    data: {
                                        action: 'AWARD_DONE'
                                    },
                                    success: function (xhr) {
                                        $(".rotateImg").addClass('rotateImgNo');
                                        if (xhr.left >= 0) {
                                            if (xhr.left >= 0) {
                                                if (xhr.amount == 50.00) {
                                                    index = 3
                                                } else if (xhr.amount == 200.00) {
                                                    index = 2
                                                } else if (xhr.amount == 500.00) {
                                                    index = 1
                                                } else if (xhr.amount == 1000.00) {
                                                    index = 0
                                                }
                                                var a = runzp(index);
                                                $('.rotateImg').rotate({
                                                    duration: 3000,
                                                    angle: 0,
                                                    animateTo: 1440 + a.angle,
                                                    callback: function () {
                                                        $('.page,.winningDiv').show();
                                                        $('#moeny').text(a.prize);
                                                        var top = $('.zhuanpanDiv').offset().top;
                                                        var left = $('.zhuanpanDiv').offset().left;
                                                        $('.winningDiv').css({
                                                            'top': top,
                                                            'left': left
                                                        })
                                                        $('.page').width(document.body.clientWidth);
                                                        $('.page').height(document.body.clientHeight);
                                                        $(".rotateImg").removeClass('rotateImgNo');
                                                    }
                                                });
                                            } else {
                                                $('.errorWin').find('#errorContent').text('抱歉～您不符合参加规则');
                                                alert($('.errorWinDiv').html())
                                            }
                                        }
                                    }
                                })
                            } else {
                                $('.errorWin').find('#errorContent').text('抱歉～您不符合参加规则');
                                alert($('.errorWinDiv').html())
                            }
                        }
                    }
                }
            });
        },
        //页面初始化
        _aboutPageFun:function(){
            $('.bannerFonts').addClass('bannerFontsHover');
            //关闭中奖遮罩
            $('.spanBtn,.againBtn').on('click',function(){
                $('.page,.winningDiv').hide();
            })
            //非法用户
            $('#checkUserStatus').on('click',function(){
                if($(this).hasClass('newUser')){
                  $('.errorWin').find('#errorContent').text('不能重复领取～亲');
                }else{
                  $('.errorWin').find('#errorContent').text('抱歉～您不符合参加规则');
                }
                alert($('.errorWinDiv').html())
            })
            //初始化数据
            org.ajax({
                url: '/api/celebrate/awards/',
                type: "POST",
                data: {
                    action: 'IS_VALID'
                },
                success: function (xhr) {
                    //有效用户
                    if (xhr.ret_code == '3001') {
                        org.ajax({
                            url: '/api/celebrate/awards/',
                            type: "POST",
                            data: {
                                action: 'ENTER_WEB_PAGE'
                            },
                            success: function (xhr) {
                                left = xhr.left;
                            }
                        })
                        $('#checkUserStatus').addClass('newUser')
                    } else if (xhr.ret_code == '3000') {
                        //非法用户
                        $('#checkUserStatus').addClass('oldUser')
                    }
                }
            })
        },
        _winningList:function(){
            org.ajax({
                url: '/api/celebrate/awards/',
                type: "POST",
                data: {
                    action: 'GET_AWARD'
                },
                async: false,
                success: function (xhr) {
                    var htmlStr = '';
                    if (xhr.data.length > 0) {
                        $.each(xhr.data, function (i, o) {
                            i % 2 == 0 ? oddStyle = 'odd' : oddStyle = '';
                            ;
                            htmlStr += '<li class=' + oddStyle + '><span>恭喜<em>' + o.phone.substring(0, 3) + '****' + o.phone.substring(8, 12) + '</em>获得</span><label>' + o.awards + '元红包</label></li>'
                        })
                        $('#users').append(htmlStr);
                    }
                }
            })
        }
    }
    return {
        init : lib.init
    }
})(org);

org.anniversaryWap = (function(org){
    var lib = {
        init:function(){
            $('.bannerFonts').addClass('bannerFontsHover');
            $('.rotateImg').on('click',function(){
                 alert($('.errorWinDiv').html())
            })
            //无线滚动
            var timer,i= 1,j=2;
            timer=setInterval(function(){
              if (-parseInt($('#users').css('top'))>=$('#users li').height()){
                $('#users li').eq(0).appendTo($('#users'));
                $('#users').css({'top':'0px'})
                i=0
              }else{
                i++
                $('#users').css({'top':-i+'px'})
              }
            },30)
        }
    }
    return {
        init : lib.init
    }
})(org);


;(function(org){
    $.each($('script'), function(){
        var src = $(this).attr('src');
        if(src && src.indexOf(org.scriptName) > 0){
            if($(this).attr('data-init') && org[$(this).attr('data-init')]){
                org[$(this).attr('data-init')].init();
            }
        }
    })
})(org);
