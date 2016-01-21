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
            if(difference == 2){
                strHtml = "<div id='alertTxt' class='popub-txt investWin'><p><img src='/static/imgs/mobile_activity/app_experience/right.png'/></p>";
                strHtml+="<p class='successFonts'>恭喜您投资成功！</p><p>到期后体验金自动收回</p><p>收益自动发放</p></div>";
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
                    org.experience.init()
                }
            })
        }
        mixins.sendUserInfo(function (data) {
            if (data.ph == '') {
                login = false;
                mixins.loginApp({refresh:1, url:''});
            } else {
                login = true;
                connect(data)
                mixins.sendUserInfo('is_authenticated','')
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
            lib._goInvest()
        },
        _goInvest: function () {
            /*投资*/
            $('.accountInvestBtn').on('click', function () {
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
                                location.reload();
                            }, 2000)
                        }
                    },
                    error: function (data) {
                        org.ui.alert(data.message, '', '4')
                    }
                });
            })
        }
    }
    return {
        init: lib.init
    }
})(org);
$.each($('script'), function(){
    var src = $(this).attr('src');
    if(src){
        if($(this).attr('data-init') && org[$(this).attr('data-init')]){
            org[$(this).attr('data-init')].init();
        }
    }
})