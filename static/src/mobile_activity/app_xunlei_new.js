var count = 0, timer;
org.ui = (function(){
    var lib = {
        _alert: function(txt, callback,btn){
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
            strHtml = "<div class='xunlei-alert'>"+ txt +"<p class='popub-footer'><div class='close_btn close-alert'>"+ btn +"</div><div class='cha'></div></div>";
            alertFram.innerHTML = strHtml;
            document.body.appendChild(alertFram);
            document.body.appendChild(shield);

            $('.close_btn,.cha').on('click',function(){
                alertFram.style.display = "none";
                shield.style.display = "none";
                callback && callback();
                count = 0;
            })
            document.body.onselectstart = function(){return false;};
        }
    }

    return {
        alert : lib._alert
    }
})();
org.xunlei = (function(org){
    var lib = {
        init:function(){
            lib._newUserReward();
            lib._getWinList();
            lib._getRewardCount();
            //lib._listScroll();
            lib._luckDraw();
        },
        _newUserReward : function(){
           $('#rewardDetail').on('click',function(){
                var ele = $('.explain-min');
                var curHeight = ele.height()
                var autoHeight = ele.css('height', 'auto').height();
                if (!ele.hasClass('down')){
                  ele.height(curHeight).animate({height: autoHeight},500,function(){
                    ele.addClass('down')
                  });
                }else{
                  ele.height(curHeight).animate({height: 0},500,function(){
                    ele.removeClass('down')
                  });
                }
            })
        },
        _getWinList : function(){
              org.ajax({
                url: '/api/xunlei/treasure/',
                dataType: 'json',
                type: 'GET',
                data: {
                    type: 'orders'
                },
                success: function (data) {
                    if (data.data == '') {
                        $('.win-box').hide()
                    } else {
                        $('.win-box').show()
                        var str = '';
                        $.each(data.data, function (i, o) {
                            if (o.awards > 2) {
                                var strs = '<span>' + o.awards + '元</span>  体验金'
                            } else {
                                var strs = '<span>' + o.awards + '%</span>  加息券'
                            }
                            str += '<li>恭喜 ' + o.phone + ' 用户，获得 ' + strs + '</li>'
                        })
                        $('#winList').append(str);
                        if(data.data.length > 2){
                            lib._listScroll();
                        }
                    }
                }
            })
        },
        _getRewardCount : function(){
            org.ajax({
                url: '/api/xunlei/treasure/',
                dataType: 'json',
                type: 'GET',
                data: {
                    type: 'chances'
                },
                success: function (data) {
                    $('#lotteryCounts').text(data.lefts);
                }
            })
        },
        _listScroll : function(){
            var i= 1,j=2;
            timer=setInterval(function(){
                if (-parseInt($('#winList').css('top'))>=$('#winList li').height()){
                    $('#winList li').eq(0).appendTo($('#winList'));
                    $('#winList').css({'top':'0px'})
                    i=0
                }else{
                    i++
                    $('#winList').css({'top':-i+'px'});
                }
            },30)
        },
        _luckDraw : function(){
            $('.people-icon').on('click',function(){
                var self = $(this);
                if(count == 0) {
                    count = 1;
                    org.ajax({
                        url: '/api/xunlei/treasure/',
                        dataType: 'json',
                        type: 'post',
                        data: {},
                        success: function (data) {
                            if (data.code == 1002) {
                                $('#lotteryCounts').text(0);
                                org.ui.alert('<div class="two-line-sty"><p class="mtO">客官，您的挖奖机会已经用光！</p></div>', '', '知道了')
                            } else if (data.code == 0) {
                                $('#lotteryCounts').text(data.lefts);
                                setTimeout(function () {
                                    self.addClass('people-icon2');
                                    setTimeout(function () {
                                        self.addClass('people-icon3');
                                        setTimeout(function () {
                                            self.removeClass('people-icon2 people-icon3');
                                            if (data.type == '加息券') {
                                                org.ui.alert('<div class="two-line-sty"><p>人品大爆发，' + data.amount + '%加息券已经悄悄的在您的账户中！</p></div>', '', '太棒了')
                                            } else {
                                                org.ui.alert('<div class="two-line-sty"><p>人世间最美好的事情莫不过如此，' + data.amount + '元体验金已经在您的账户中！</p></div>', '', '太棒了')
                                            }
                                            lib._getWinList();
                                            clearInterval(timer);
                                        }, 200)
                                    }, 500)
                                }, 300)
                            } else if (data.code == 1) {
                                $('#lotteryCounts').text(data.lefts);
                                var array = ['<p>佛说：前世的500次回眸<br/>才换得今世的一次中奖，淡定！</p>', '<p class="mtO">大奖何时有？把酒问青天！</p>', '<p class="mtO">大奖下回见，网利宝天天见！</p>'],
                                    random = parseInt(3 * Math.random());
                                org.ui.alert('<div class="two-line-sty">' + array[random] + '</div>', '', '再试一次')
                            }
                        }
                    })
                }
            })
        }
    }
    return {
        init : lib.init
    }
})(org);
;(function(org){
    $.each($('script'), function(){
        var src = $(this).attr('src');
        if(src){
            if($(this).attr('data-init') && org[$(this).attr('data-init')]){
                org[$(this).attr('data-init')].init();
            }
        }
    })
})(org);