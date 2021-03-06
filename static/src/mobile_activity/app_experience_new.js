org.ui = (function(){
    var lib = {
        _alert: function(txt, callback,difference, tag){
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
            if(difference == 2){
                strHtml = "<div id='alertTxt' class='popub-txt investWin'><p><img src='/static/imgs/mobile_activity/app_experience/right.png'/></p>";
                strHtml+="<p class='successFonts'>恭喜您投资成功！</p><p>到期后体验金自动收回</p><p>收益自动发放</p></div>";
            }else if(difference == 4){
                if(tag == 'goRecharge'){
                    var btnTxt = '去充值',recharge = 'goRecharge',closeBtns = '<div class="close-red"></div>';
                }else{
                    var btnTxt = '知道了',recharge = '',closeBtns = '';
                }
                strHtml ="<div id='alertTxt' class='popub-txt oldUserWin'><p class='p_center'>"+ txt +"</p>";
                strHtml+="<p><img src='/static/imgs/mobile_activity/app_experience/logo_new.png'/></p><p class='popub-footer'><div class='close_btn "+ recharge +"'>"+ btnTxt +"！</div></p>"+ closeBtns +"</div>";
            }
            alertFram.innerHTML = strHtml;
            document.body.appendChild(alertFram);
            document.body.appendChild(shield);

            $('.close_btn,.close-red').on('click',function(){
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

org.investment = (function (org) {
    var lib = {
        init: function () {
            lib._investmentFun();
        },
        _investmentFun: function () {
            $('#rzTyj').on('click',function(){
                org.ajax({
                    url: '/api/experience/buy/',
                    type: 'POST',
                    data: {},
                    success: function (data) {
                        if (data.ret_code > 0) {
                            if(data.ret_code == 30009){
                                org.ui.alert(data.message, '', '4', 'goRecharge')
                            }else{
                                org.ui.alert(data.message, '', '4')
                            }
                        } else {
                            org.ui.alert('', '', '2')
                            setTimeout(function () {
                                $('#alert-cont,#popubMask').hide();
                                location.reload();
                            }, 2000)
                        }
                    },
                    error: function (data) {
                        org.ui.alert(data.message, '', '4')
                    }
                })
            })
        }
    }
    return {
        init: lib.init
    }
})(org);

;(function(org) {
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
                        org.investment.init()
                    }
                })
            }

            mixins.sendUserInfo(function (data) {
                if (data.ph == '') {
                } else {
                    connect(data)
                    $('body').on('click','.goRecharge,#recharge',function(){
                        mixins.rechargeApp({
                            refresh: 1,
                            url: 'https://www.wanglibao.com/activity/experience/mobile/'
                        })
                    })
                }
            })
        },
        other: function () {
            org.investment.init();
            $('body').on('click','.goRecharge,#recharge',function(){
                console.log(1)
                window.location.href = '/weixin/recharge/';
            })
        }
    })
})(org);
