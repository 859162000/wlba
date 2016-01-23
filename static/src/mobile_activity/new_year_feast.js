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
                var strHtml = "<div id='packets' class='packets clearfix'><div class='packets-bg'><div class='packets-content'>"+ txt +"</div></div>"
                            +"<p class='yellow-fonts'>领取成功！</p><p class='yellow-fonts'>进去“我的账户”－－“理财卷”及“体验金专区”查看</p>"
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
            lib._arrowStyle(1,'default');
            lib._potAward();
            lib._lookMoreInfoFun();
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
                 if($('.authenticated').length > 0){
                    if(!$('.pot-s').hasClass('selectEd')){
                         var index = $(this).attr('index');
                         var i = 1,j = 0;
                         var timer = setInterval(function(){
                            i == 4 ? i = 0 : i = i;
                            if((j>3) && (i == (index - 1))){
                                clearInterval(timer);
                                //<p>150元红包</p><p>400元红包</p><p>1%加息券</p><p>1.8%加息券</p><p>888元体验金</p>
                                setTimeout(function(){
                                    var txt = '<p>100元红包</p><p>300元红包</p><p>1.2%加息券</p><p>2%加息券</p><p>888元体验金</p>';
                                    org.ui.alert(txt, '', '2')
                                },500)
                            }
                            lib._arrowStyle(i+1)
                            i++,j++;
                         },500)
                         $('.pot-s').addClass('selectEd')
                     }
                 }else{
                     window.location.href = '/weixin/login/?next=/activity/new_year_feast/';
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
                window.location.href = '/weixin/list/?next=/activity/new_year_feast/';
            })
        },
        _receiveFun: function(){
            $('.packets-btn a').click(function(){
                if($('.authenticated').length > 0) {
                    var txt = '<p class="title-s">领取成功！</p><p class="pop-fonts">进去“我的账户”－－“理财卷”及“体验金专区”查看</p>'
                    org.ui.alert(txt, '', '3')
                }else{
                    window.location.href = '/weixin/login/?next=/activity/new_year_feast/';
                }
            })
        }
    }
    return {
        init: lib.init
    }
})(org);
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
            if (data.ph == '') {
                $('.pot-s,.packets-btn a').on('click',function(){
                    mixins.loginApp({refresh: 1, url: ''})
                })
                $('#projectList').on('click',function(){
                    mixins.jumpToManageMoney()
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