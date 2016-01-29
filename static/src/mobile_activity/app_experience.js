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
                shield.style.cssText="position:fixed;bottom:0;top:0;width:100%; background:rgba(0,0,0,0.5); z-index:1000000;height:100%";
                alertFram = document.createElement("DIV");
                alertFram.id="alert-cont";
            }
            if(difference == 1){
                alertFram.style.cssText = "position:fixed; top:35%;left:0; width:100%;z-index:1000001;";
                strHtml = "<div id='alertTxt' class='popub-txt successWin'>";
                strHtml+="<div class='winContent'><p class='qianshu'>28888<span>元</span></p><p class='con1'>恭喜您获得</p><p class='con2'>28,888元体验金</p><div class='btns popub-footer'><a href='javascript:void(0)' class='close_btn'>领完可以在这里投资呦！</a></div></div></div>";
            }else if(difference == 2){
                strHtml = "<div id='alertTxt' class='popub-txt investWin'><p><img src='/static/imgs/mobile_activity/app_experience/right.png'/></p>";
                strHtml+="<p class='successFonts'>恭喜您投资成功！</p><p>到期后体验金自动收回</p><p>收益自动发放</p></div>";
            }else if(difference == 3){
                strHtml = "<div id='alertTxt' class='popub-txt oldUserWin'><p class='p_left'>体验金由系统自动发放，</p>";
                strHtml+="<p class='p_left'>请继续关注网利宝最新活动。</p>";
                strHtml+="<p><img src='/static/imgs/mobile_activity/app_experience/logo.png'/></p><p class='popub-footer'><div class='close_btn'>知道了！</div></p></div>";
            }else if(difference == 4){
                strHtml ="<div id='alertTxt' class='popub-txt oldUserWin'><p class='p_center'>"+ txt +"</p>";
                strHtml+="<p><img src='/static/imgs/mobile_activity/app_experience/logo.png'/></p><p class='popub-footer'><div class='close_btn'>知道了！</div></p></div>";
            }
            alertFram.innerHTML = strHtml;
            document.body.appendChild(alertFram);
            document.body.appendChild(shield);

            $('.close_btn').on('click',function(){
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
var login = false;
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
                    org.experience.init()
                }
            })
        }
        mixins.sendUserInfo(function (data) {
            if (data.ph == '') {
                login = false;
                $('#nologin').unbind('click')
                $('.receive_box').on('click', function(){
                    mixins.registerApp({refresh:1, url:''});
                })
            } else {
                login = true;
                connect(data)
            }
        })
    },
    other: function(){
        org.experience.init()
    }
})


org.experience = (function (org) {
    var lib = {
        init: function () {
            lib._lookMore()
            lib._goExperienceBtn()
            lib._goInvest()
        },
        _lookMore: function () {
           $('#nologin').on('click', function () {
                window.location.href = '/weixin/regist/?next=/activity/experience/mobile/';
           })
            $lookMore = $('#lookMore')
            $lookMore.on('click', function () {
                var ele = $('.history-list');
                var curHeight = ele.height();
                var autoHeight = ele.css('height', 'auto').height();
                if (!ele.hasClass('down')) {
                    ele.height(curHeight).animate({height: autoHeight}, 500, function () {
                        ele.addClass('down')
                    });
                } else {
                    ele.height(curHeight).animate({height: 0}, 500, function () {
                        ele.removeClass('down')
                    });
                }
            })
        },
        _goExperienceBtn: function () {
            //goExperienceBtn 新用户领取成功
            $goExperienceBtn = $('.no_invest');
            $goExperienceBtn.on('click', function () {
                org.ajax({
                    url: '/api/experience/get_experience/',
                    type: 'POST',
                    data: {},
                    success: function (data) {
                        if (data.ret_code == 0) {
                            org.ui.alert('', function () {
                                $('body,html').scrollTo($('.project').offset().top);
                            }, '1')
                            var tyjye = lib._fmoney((parseFloat($('.tyjye').text()) + data.data.amount), 2);
                            var zzc = lib._fmoney((parseFloat($('.zzc').text()) + data.data.amount), 2);
                            var rzje = lib._fmoney(data.data.amount, 2, 1);
                            $('.qianshu').html(data.data.amount + '<span>元</span>')
                            $('.icon2').text(rzje + '元体验金')
                            $('.tyjye').text(tyjye);
                            $('.zzc').text(zzc);
                            $('.rzje').text(rzje + '元');
                            $('.investBtnEd').removeClass('investBtnEd').addClass('investBtn');
                            $('.receive_box').find('img').hide();
                            $('.receive_box').find('#edT').show().text('已领取体验金' + data.data.amount + '元')
                        } else {
                            org.ui.alert(data.message, '', '4')
                        }
                    },
                    error: function (data) {
                        org.ui.alert(data.message, '', '4')
                    }
                });
            })
            //老用户
            $('.investeds').on('click', function () {
                org.ui.alert('', '', '3')
            })
        },
        _goInvest: function () {
            /*投资*/
            $('.project_btn').delegate('.investBtn', 'click', function () {
                org.ajax({
                    url: '/api/experience/buy/',
                    type: 'POST',
                    data: {},
                    success: function (data) {
                        if (data.ret_code > 0) {
                            org.ui.alert(data.message, '', '4')
                        } else {
                            org.ui.alert('', '', '2')
                            setTimeout(function () {
                                $('#alert-cont,#popubMask').hide();
                                /*$('.investBtn').text('已投资'+ data.data.amount +'元').addClass('investBtnEd').removeClass('investBtn')
                                 $('.time_style').show().text('将于'+ data.data.term_date +'收益'+ data.data.interest +'元')*/
                                location.reload();
                            }, 2000)
                        }
                    },
                    error: function (data) {
                        org.ui.alert(data.message, '', '4')
                    }
                });
            })
        },
        /*格式化金额*/
        _fmoney: function (s, n, m) {
            n = n > 0 && n <= 20 ? n : 2;
            s = parseFloat((s + "").replace(/[^\d\.-]/g, "")).toFixed(n) + "";
            var l = s.split(".")[0].split("").reverse(),
                r = s.split(".")[1];
            t = "";
            for (i = 0; i < l.length; i++) {
                t += l[i] + ((i + 1) % 3 == 0 && (i + 1) != l.length ? "," : "");
            }
            if (m == 1 && r == '00') {
                return t.split("").reverse().join("");
            } else {
                return t.split("").reverse().join("") + "." + r;
            }
        }
    }
    return {
        init: lib.init
    }
})(org);
;(function(org){
    $.extend($.fn, {
        scrollTo: function(m){
            var n = 0, timer = null, that = this;
            var smoothScroll = function(m){
                var per = Math.round(m / 50);
                n = n + per;
                if(n > m){
                    window.clearInterval(timer);
                    return false;
                }
                that.scrollTop(n);
            };

            timer = window.setInterval(function(){
                smoothScroll(m);
            }, 20);
        }
   })
        /*效果*/
    function snow(left, height, src) {
        var elem = $("<div />", {
            css: {
                left: left + "px",
                height: height + "px"
            }
        }).addClass('div').append($('<img />', {
            src: src
        }).addClass('roll'));
        $('#showMoney').append(elem);
        setTimeout(function () {
            $(elem).remove();
        }, 4000);
    }

    xg = setInterval(function () {
        var left = Math.random() * window.innerWidth;
        var height = Math.random() * window.innerHeight;
        var src = "/static/imgs/mobile_activity/app_experience/xg" + Math.floor(Math.random() * 7 + 1) + ".png";
        snow(left, height, src);
    }, 300);

    $(window).scroll(function () {
        if ($('body').scrollTop() > 0) {
            $('#showMoney').animate({opacity: 0}, 500);
        } else {
            $('#showMoney').animate({opacity: 1}, 500);
        }
    });
})(org);