
var org = (function(){
    document.body.addEventListener('touchstart', function () { }); //ios 触发active渲染
    var lib = {
        scriptName: 'app_fullpage.js',
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

            dom.on('input', function() {
                _inputCallback();
            });

            function _inputCallback(){
                var earning, earning_element, earning_elements, fee_earning;
                var target = $('input[data-role=p2p-calculator]'),
                    existing = parseFloat(target.attr('data-existing')),
                    period = target.attr('data-period'),
                    rate = target.attr('data-rate')/100,
                    pay_method = target.attr('data-paymethod');
                    activity_rate = target.attr('activity-rate')/100;
                    activity_jiaxi = target.attr('activity-jiaxi')/100;
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

                for (var i = 0; i < earning_elements.length; i ++) {
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

org.ui = (function(){
    var lib = {
        _alert: function(txt, callback){
            if(document.getElementById("alert-cont")){
                document.getElementById("alertTxt").innerHTML = txt;
                document.getElementById("popubMask").style.display = "block";
                document.getElementById("alert-cont").style.display = "block";
            }else{
                var shield = document.createElement("DIV");
                shield.id = "popubMask";
                shield.style.cssText="position:absolute;bottom:0;top:0;width:100%; background:rgba(0,0,0,0.5); z-index:1000000;";
                var alertFram = document.createElement("DIV");
                alertFram.id="alert-cont";
                alertFram.style.cssText="position:absolute; top:35%;left:50%; width:14rem; margin:-2.75rem 0 0 -7rem; background:#fafafa; border-radius:.3rem;z-index:1000001;";
                strHtml = "<div id='alertTxt' class='popub-txt' style='color:#333;font-size: .9rem!important;padding: 1.25rem .75rem;'>"+txt+"</div>";
                strHtml += " <div class='popub-footer' style='width: 100%;padding: .5rem 0;font-size: .9rem;text-align: center;color: #4391da;border-top: 1px solid #d8d8d8;border-bottom-left-radius: .25rem;border-bottom-right-radius: .25rem;'>确认</div>";
                alertFram.innerHTML = strHtml;
                document.body.appendChild(alertFram);
                document.body.appendChild(shield);

                $('.popub-footer').on('click',function(){
                    alertFram.style.display = "none";
                    shield.style.display = "none";
                    callback && callback();
                })
            }
            document.body.onselectstart = function(){return false;};
        },
        _showSign:function(signTxt, callback){
            var $sign = $('.error-sign');
            if($sign.length == 0){
                $('body').append("<section class='error-sign'>" + signTxt + "</section>");
                $sign = $('.error-sign');
            }else{
                $sign.text(signTxt)
            }
            ~function animate(){
                $sign.css('display','block');
                setTimeout(function(){
                    $sign.css('opacity', 1);
                    setTimeout(function(){
                        $sign.css('opacity', 0);
                        setTimeout(function(){
                            $sign.hide();
                            return callback && callback();
                        },300)
                    },1000)
                },0)
            }()
        },
        /*
          .form-list
              .form-icon.user-phone(ui targer).identifier-icon（事件target）
              .form-input
                input(type="tel", name="identifier", placeholder="请输入手机号",data-target2='identifier-icon'（事件target）, data-icon='user-phone'(ui事件), data-target="identifier-edit"(右侧操作), data-empty=''（input val空的时候的classname）, data-val='input-clear'（input val不为空的时候的classname）).foreach-input
                .form-edit-icon.identifier-edit（右边操作如：清空密码）
         */
        _inputStyle:function(options){
            var $submit = options.submit,
                inputArrList = options.inputList;

            $.each(inputArrList, function(i){
                inputArrList[i]['target'].on('input',function(){
                    var $self = $(this);
                    if($self.val() == ''){
                        inputForClass([
                            { target: $self.attr('data-target'), addName : $self.attr('data-empty'), reMove : $self.attr('data-val')},
                            { target: $self.attr('data-target2'), addName : $self.attr('data-icon'), reMove : ($self.attr('data-icon')+"-active")},
                        ])
                        $submit.attr('disabled', true);
                    }else{
                        inputForClass([
                            { target: $self.attr('data-target'), addName : $self.attr('data-val'),reMove : $self.attr('data-empty')},
                            { target: $self.attr('data-target2'), addName : ($self.attr('data-icon')+"-active"), reMove : $self.attr('data-icon')}
                        ])
                    }
                    canSubmit() ? $submit.css('background','rgba(219,73,63,1)').removeAttr('disabled') : $submit.css('background','rgba(219,73,63,.5)').attr('disabled')
                })
            })

            //用户名一键清空
            $('.identifier-edit').on('click', function(e){
                $(this).siblings().val('').trigger('input');
            })
            //密码隐藏显示
            $('.password-handle').on('click',function(){
                if($(this).hasClass('hide-password')){
                    $(this).addClass('show-password').removeClass('hide-password');
                    $(this).siblings().attr('type','text');
                }else if($(this).hasClass('show-password')){
                    $(this).addClass('hide-password').removeClass('show-password');
                    $(this).siblings().attr('type','password');
                }
            })

            var inputForClass = function(ops){
                if(!typeof(ops) === 'object') return ;
                $.each(ops, function(i){
                    $('.'+ops[i].target).addClass(ops[i].addName).removeClass(ops[i].reMove);
                })
            }
            var returnCheckArr = function(){
                var returnArr = [];
                for(var i = 0; i < arguments.length; i++){
                    for(var arr in arguments[i]){
                        if(arguments[i][arr]['required'])
                          returnArr.push(arguments[i][arr]['target'])
                    }
                }
                return returnArr
            }
            var canSubmit = function(){
                var isPost = true, newArr = [];

                newArr = returnCheckArr(options.inputList, options.otherTarget);

                $.each(newArr, function(i, dom){
                    if(dom.attr('type') == 'checkbox'){
                        if (!dom.attr('checked'))
                            return  isPost =  false
                    }else if (dom.val() == '')
                        return  isPost =  false
                })

                return isPost
            }
        },
    }

    return {
        focusInput: lib._inputStyle,
        showSign : lib._showSign,
        alert : lib._alert,
    }
})();

org.fullpage = (function(org){
    var lib ={
        weiURL: '/weixin/api/jsapi_config/',
        init :function(){
            lib._every();
            lib._share();
        },
        _every :function(){
          var _ = $('#fullpage-warp'), loading = $('#loadPage'), arrow = $('#arrow'),
              play = $('#play'), music = document.getElementById('music');

          play.on('click', function(e){
              if (music.paused) {
                  music.play();
                  play.addClass('play').removeClass('close');
              } else {
                  music.pause();
                  play.addClass('close').removeClass('play');
              }
          })

          music.play();
          $(document).one('touchstart', function(){
              music.play();
          })

          _.fullpage({

              page: '.page',

              change: function (data) {
                  data.cur + 1 === _.find('.page').size() ? arrow.hide() : arrow.show();
              }

          });

          var queue = new createjs.LoadQueue();

          queue.on('progress', function () {

              var num = Math.floor(queue.progress * 100);
              $('.process').text(num + '%');

          }, this);

          queue.on('complete', function () {

              loading.remove();

          }, this);

          queue.loadManifest([
              {id: 'image1', src: '/static/imgs/mobile_activity/app_fullpage/music.png'},
              {id: 'image2', src: '/static/imgs/mobile_activity/app_fullpage/arrow.png'},
              {id: 'image3', src: '/static/imgs/mobile_activity/app_fullpage/first_page.jpg'},
              {id: 'image4', src: '/static/imgs/mobile_activity/app_fullpage/first_title320.png'},
              {id: 'image5', src: '/static/imgs/mobile_activity/app_fullpage/me_1.jpg'},
              {id: 'image6', src: '/static/imgs/mobile_activity/app_fullpage/me_2.jpg'},
              {id: 'image7', src: '/static/imgs/mobile_activity/app_fullpage/me_mask.png'},
              {id: 'image8', src: '/static/imgs/mobile_activity/app_fullpage/me_4.png'},
              {id: 'image9', src: '/static/imgs/mobile_activity/app_fullpage/me_5.png'},
              {id: 'image10', src: '/static/imgs/mobile_activity/app_fullpage/me_3.png'},
              {id: 'image11', src: '/static/imgs/mobile_activity/app_fullpage/me_tit2.png'},
              {id: 'image12', src: '/static/imgs/mobile_activity/app_fullpage/j_1.jpg'},
              {id: 'image13', src: '/static/imgs/mobile_activity/app_fullpage/j_2.jpg'},
              {id: 'image14', src: '/static/imgs/mobile_activity/app_fullpage/j_3.png'},
              {id: 'image15', src: '/static/imgs/mobile_activity/app_fullpage/j_4.png'},
              {id: 'image16', src: '/static/imgs/mobile_activity/app_fullpage/j_mask.png'},
              {id: 'image17', src: '/static/imgs/mobile_activity/app_fullpage/j_title1.png'},
              {id: 'image18', src: '/static/imgs/mobile_activity/app_fullpage/j_title2.png'},
              {id: 'image19', src: '/static/imgs/mobile_activity/app_fullpage/j_title3.png'},

              {id: 'image20', src: '/static/imgs/mobile_activity/app_fullpage/t_1.jpg'},
              {id: 'image21', src: '/static/imgs/mobile_activity/app_fullpage/t_2.jpg'},
              {id: 'image22', src: '/static/imgs/mobile_activity/app_fullpage/t_3.png'},
              {id: 'image23', src: '/static/imgs/mobile_activity/app_fullpage/t_mask.png'},
              {id: 'image24', src: '/static/imgs/mobile_activity/app_fullpage/t_title1.png'},
              {id: 'image25', src: '/static/imgs/mobile_activity/app_fullpage/t_title2.png'},

              {id: 'image26', src: '/static/imgs/mobile_activity/app_fullpage/m_1.jpg'},
              {id: 'image27', src: '/static/imgs/mobile_activity/app_fullpage/m_2.jpg'},
              {id: 'image28', src: '/static/imgs/mobile_activity/app_fullpage/m_3.png'},
              {id: 'image29', src: '/static/imgs/mobile_activity/app_fullpage/m_4.png'},
              {id: 'image30', src: '/static/imgs/mobile_activity/app_fullpage/m_mask.png'},
              {id: 'image31', src: '/static/imgs/mobile_activity/app_fullpage/m_title1.png'},
              {id: 'image32', src: '/static/imgs/mobile_activity/app_fullpage/m_title2.png'},

              {id: 'image33', src: '/static/imgs/mobile_activity/app_fullpage/q_1.jpg'},
              {id: 'image34', src: '/static/imgs/mobile_activity/app_fullpage/q_2.jpg'},
              {id: 'image35', src: '/static/imgs/mobile_activity/app_fullpage/q_3.png'},
              {id: 'image36', src: '/static/imgs/mobile_activity/app_fullpage/q_4.png'},
              {id: 'image37', src: '/static/imgs/mobile_activity/app_fullpage/q_mask.png'},
              {id: 'image38', src: '/static/imgs/mobile_activity/app_fullpage/q_title1.png'},
              {id: 'image39', src: '/static/imgs/mobile_activity/app_fullpage/q_title2.png'},
              {id: 'image40', src: '/static/imgs/mobile_activity/app_fullpage/last_titi3.png'},

              {id: 'image41', src: '/static/imgs/mobile_activity/app_fullpage/last_logo.png'},
              {id: 'image42', src: '/static/imgs/mobile_activity/app_fullpage/last_titi2.png'},
              {id: 'image43', src: '/static/imgs/mobile_activity/app_fullpage/last_erweima.png'},
              {id: 'image44', src: '/static/imgs/mobile_activity/app_fullpage/last_footer.png'},

          ]);

        },
        /*
        * 微信分享
         */
        _share: function(){
            var jsApiList = ['scanQRCode', 'onMenuShareAppMessage','onMenuShareTimeline','onMenuShareQQ',];
            org.ajax({
                type : 'GET',
                url : lib.weiURL,
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

                var host = 'https://www.wanglibao.com',
                    shareImg = host + '/static/imgs/mobile/share_logo.png',
                    shareLink = host + '/activity/app_fullpage/',
                    shareMainTit = '你喜欢什么样的自己？',
                    shareBody = '网利宝一周年啦！';
                //分享给微信好友
                org.onMenuShareAppMessage({
                    title: shareMainTit,
                    desc: shareBody,
                    link: shareLink,
                    imgUrl: shareImg
                });
                //分享给微信朋友圈
                org.onMenuShareTimeline({
                    title: shareMainTit,
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
        },
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
