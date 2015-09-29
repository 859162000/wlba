$(function(){
    var loading = $('#loadPage');

        var queue = new createjs.LoadQueue();
        queue.on('progress', function () {
            var num = Math.floor(queue.progress * 100);
            $('.process').text(num + '%');
        }, this);
        queue.on('complete', function () {
            loading.remove();

        }, this);
        queue.loadManifest([
            {id: 'image1', src: '/static/imgs/mobile_activity/app_ten_year/bg.jpg'},
            {id: 'image2', src: '/static/imgs/mobile_activity/app_ten_year/big_theme.png'},
            {id: 'image3', src: '/static/imgs/mobile_activity/app_ten_year/mask.png'},
            {id: 'image4', src: '/static/imgs/mobile_activity/app_ten_year/meteor1.png'},
            {id: 'image5', src: '/static/imgs/mobile_activity/app_ten_year/meteor2.png'},
            {id: 'image6', src: '/static/imgs/mobile_activity/app_ten_year/music.png'},
            {id: 'image7', src: '/static/imgs/mobile_activity/app_ten_year/page1_text1.png'},
            {id: 'image8', src: '/static/imgs/mobile_activity/app_ten_year/page1_text2.png'},
            {id: 'image9', src: '/static/imgs/mobile_activity/app_ten_year/page2_img1.png'},
            {id: 'image10', src: '/static/imgs/mobile_activity/app_ten_year/page2_img2.png'},
            {id: 'image11', src: '/static/imgs/mobile_activity/app_ten_year/page2_img11.png'},
            {id: 'image12', src: '/static/imgs/mobile_activity/app_ten_year/page2_img21.png'},
            {id: 'image13', src: '/static/imgs/mobile_activity/app_ten_year/page2_shadow.png'},
            {id: 'image14', src: '/static/imgs/mobile_activity/app_ten_year/page2_text.png'},
            {id: 'image15', src: '/static/imgs/mobile_activity/app_ten_year/page3_boy.png'},
            {id: 'image16', src: '/static/imgs/mobile_activity/app_ten_year/page3_boy2.png'},
            {id: 'image17', src: '/static/imgs/mobile_activity/app_ten_year/page3_line.png'},
            {id: 'image18', src: '/static/imgs/mobile_activity/app_ten_year/page3_man.png'},
            {id: 'image19', src: '/static/imgs/mobile_activity/app_ten_year/page3_talk.png'},
            {id: 'image20', src: '/static/imgs/mobile_activity/app_ten_year/page4_line.png'},
            {id: 'image21', src: '/static/imgs/mobile_activity/app_ten_year/page4_man1.png'},
            {id: 'image22', src: '/static/imgs/mobile_activity/app_ten_year/page4_man2.png'},
            {id: 'image23', src: '/static/imgs/mobile_activity/app_ten_year/page4_man12.png'},
            {id: 'image24', src: '/static/imgs/mobile_activity/app_ten_year/page4_math.png'},
            {id: 'image25', src: '/static/imgs/mobile_activity/app_ten_year/page4_talk.png'},
            {id: 'image26', src: '/static/imgs/mobile_activity/app_ten_year/page5_bamboo.png'},
            {id: 'image27', src: '/static/imgs/mobile_activity/app_ten_year/page5_line.png'},
            {id: 'image28', src: '/static/imgs/mobile_activity/app_ten_year/page5_talk.png'},
            {id: 'image29', src: '/static/imgs/mobile_activity/app_ten_year/page5_woman1.png'},
            {id: 'image30', src: '/static/imgs/mobile_activity/app_ten_year/page5_woman2.png'},
            {id: 'image31', src: '/static/imgs/mobile_activity/app_ten_year/page5_woman12.png'},
            {id: 'image32', src: '/static/imgs/mobile_activity/app_ten_year/page6_fly.png'},
            {id: 'image33', src: '/static/imgs/mobile_activity/app_ten_year/page6_img1.png'},
            {id: 'image34', src: '/static/imgs/mobile_activity/app_ten_year/page6_img2.png'},
            {id: 'image35', src: '/static/imgs/mobile_activity/app_ten_year/page6_text.png'},
            {id: 'image36', src: '/static/imgs/mobile_activity/app_ten_year/page7_img.png'},
            {id: 'image37', src: '/static/imgs/mobile_activity/app_ten_year/page8_text1.png'},
            {id: 'image38', src: '/static/imgs/mobile_activity/app_ten_year/page8_text2.png'},
            {id: 'image39', src: '/static/imgs/mobile_activity/app_ten_year/shadow_bottom.png'},
            {id: 'image40', src: '/static/imgs/mobile_activity/app_ten_year/slideDown.png'},
            {id: 'image41', src: '/static/imgs/mobile_activity/app_ten_year/small_theme.png'},
            {id: 'image42', src: '/static/imgs/mobile_activity/app_ten_year/ten_year.mp3'},
            {id: 'image43', src: '/static/imgs/mobile_activity/app_ten_year/logo.png'}
        ]);

    //var mp3 = document.getElementById("music"),play = $('#play');
    //play.on('click', function (e) {
    //    if (mp3.paused) {
    //        mp3.play();
    //        $('#play').addClass('play_music').removeClass('close_music');
    //    } else {
    //        mp3.pause();
    //        $('#play').addClass('close_music').removeClass('play_music');
    //    }
    //});
    //
    //mp3.play();
    //$(document).one('touchstart', function () {
    //    mp3.play();
    //});

    /*解决iphone一开始没音乐问题*/
    var g_audio = window.g_audio = new Audio();  //创建一个audio播放器
    var g_event = window.g_event =new function(){
        var events = ['load','abort','canplay','canplaythrough',
        'durationchange','emptied','ended','error',
        'loadeddata','loadedmetadata','loadstart',
        'pause','play','playing','progress',
        'ratechange','seeked','seeking','stalled',
        'suspend','timeupdate','volumechange','waiting', 'mediachange'];
        g_audio.loop = true;
        g_audio.autoplay = true;
        g_audio.isLoadedmetadata = false;
        g_audio.touchstart = true;
        g_audio.audio = true;
        g_audio.elems = {};
        g_audio.isSupportAudio = function(type){
        type=type||'audio/mpeg';
        try{
            var r=g_audio.canPlayType(type);
            return g_audio.canPlayType&&(r=='maybe'||r=='probably')
        }catch(e){return false;}
        };
        g_audio.push = function(meta){
        g_audio.previousId = g_audio.id;
        g_audio.id = meta.song_id;
        g_audio.previousSrc = g_audio.src;
        g_audio.previousTime = 0.00;
        g_audio.src = g_audio.currentSrc = meta.song_fileUrl;
        g_audio.isLoadedmetadata = false;
        g_audio.autobuffer = true;
        g_audio.load();
        g_audio.play();
        if(g_audio.previousSrc !== g_audio.src){
            g_audio.play();
        }
        };
        for(var i = 0, l = events.length; i < l; i++){
            (function(e){
                var fs = [];
                this[e] = function(fn){
                    if(typeof fn!=='function'){
                        for (var k = 0; k<fs.length; k++){
                            fs[k].apply(g_audio);
                        }
                        return ;
                    }
        fs.push(fn);
        g_audio.addEventListener(e, function(){
        fn.apply(this);
        });
        };
        }).apply(this, [events[i]]);
        }
        this.ended(function(){  //播放结束
        });
        this.load(function(){  //加载
        this.pause();
        this.play();
        });
        this.loadeddata(function(){
        this.pause();
        this.play();
        });
        this.loadedmetadata(function(){
        this.isLoadedmetadata = true;
        });
        this.error(function(){   //请求资源时遇到错误
        });
        this.pause(function(){  //歌曲暂停播放
        });
        this.play(function(){  //歌曲播放
        });
    };


        if(/i(Phone|P(o|a)d)/.test(navigator.userAgent)){
        $(document).one('touchstart', function (e) {
        g_audio.touchstart = true;
        g_audio.play();
        g_audio.pause();
        return false;
        });
        }

    //audio使用:
    $('#music').unbind('click').bind('click',function(){
    //gid 表示歌曲id,只是一个表示，没有值不影响播放
    //song_fileUrl :播放歌曲地址，不能为空，有效地址
    g_audio.elems["id"] = gid;
    g_audio.push({song_id:gid,song_fileUrl:"/static/imgs/mobile_activity/app_ten_year/ten_year.mp3"});
    });//绑定事件
    /*解决iphone一开始没音乐问题结束*/


    $('.section3 .line').load(function(){
        var s3line_height = $('.section3 .line').height();
        $('.section3 .line_img').css('height',s3line_height);
    });
    $('.section4 .line').load(function(){
        var s4line_height = $('.section4 .line').height();
        $('.section4 .line_img').css('height',s4line_height);
    });
    $('.section5 .line').load(function(){
        var s5line_height = $('.section5 .line').height();
        $('.section5 .line_img').css('height',s5line_height);
    });

    var say;
    var say_num;
    say_num = parseInt(12*Math.random());
    say_text(say_num);
    function say_text(say_num){
        switch(say_num){
            case 1:
                $('#say').text('去旅游，去邂逅');
                break;
            case 2:
                $('#say').text('少睡觉，多看书');
                break;
            case 3:
                $('#say').text('少玩游戏，多赚钱');
                break;
            case 4:
                $('#say').text('养只宠物，解解闷');
                break;
            case 5:
                $('#say').text('多锻炼，保持好身材');
                break;
            case 6:
                $('#say').text('一切都会过去，好好爱自己 ');
                break;
            case 7:
                $('#say').text('别做梦，学一项技能');
                break;
            case 8:
                $('#say').text('好好听课，不要留遗憾');
                break;
            case 9:
                $('#say').text('对自己好一点，买买买');
                break;
            case 10:
                $('#say').text('学好英语，看看世界');
                break;
            case 11:
                $('#say').text('尝试新事物，遇见新朋友');
                break;
            case 12:
                $('#say').text('再努力一下，挺住意味着一切');
                break;
        }
    }
    $('.button').click(function(){
        say = $('input').val();
        if(say==''){
            $('#name').text('自己');
        }else {
            $('#name').text(say);
        }
        $('body').unbind('touchmove');
        say_num = parseInt(18*Math.random());
        say_text(say_num);
    });

    $('#wrap').fullpage({
        anchors: ['page1','page2','page3','page4','page5','page6','page7','page8'],
        afterLoad: function(anchorLink, index) {
            if(index == 1){
                $('.section2 img').not('.slideDown').removeClass('animate');
                $('.section1 img').not('.slideDown').addClass('animate');
            }
            if(index == 2){
                $('.section1 img,.section3 img,.line_img').not('.slideDown').removeClass('animate');
                $('.section2 img').not('.slideDown').addClass('animate');
            }
            if(index == 3){
                $('.section2 img,.section4 img,.section4 .line_img').not('.slideDown').removeClass('animate');
                $('.section3 img,.section3 .line_img').not('.slideDown').addClass('animate');
            }
            if(index == 4){
                $('.section3 img,.section5 img,.section3 .line_img,.section5 .line_img').not('.slideDown').removeClass('animate');
                $('.section4 img,.section4 .line_img').not('.slideDown').addClass('animate');
            }
            if(index == 5){
                $('.shadow').animate({'opacity':'1'},500);
                $('.section4 img,.section4 .line_img,.section6 img,.section6 input').not('.slideDown').removeClass('animate');
                $('.section5 .line_img,.section5 img').not('.slideDown').addClass('animate');
            }
            if(index == 6){
                $('.shadow').animate({'opacity':'0'},500);
                $('.section7 .horn').animate({'opacity':'0'},100);
                $('.section5 img,.section5 .line_img,.section7 img,.section7 .text,.section7 .title').removeClass('animate');
                $('.section6 img,.section6 input').not('.slideDown').addClass('animate');
                say = $('input').val();
                //alert(say);
                if(say==''||say==undefined){
                    $('body').bind("touchmove", function (e) {e.preventDefault()});

                }else{
                    $('body').unbind('touchmove');
                }
            }
            if(index == 7){
                $('.section7 .horn').delay(1000).animate({'opacity':'1'},500);
                $('.section6 img,.section6 input,.section8 img,.button').not('.slideDown').removeClass('animate');
                $('.section7 img,.section7 .text,.section7 .title').not('.slideDown').addClass('animate');
            }
            if(index == 8){
                $('.section7 .horn').animate({'opacity':'0'},100);
                $('.section7 img,.section7 .text,.section7 .title').not('.slideDown').removeClass('animate');
                $('.section8 img,.button').not('.slideDown').addClass('animate');
            }
        }
    })

    var lineLink    = "https://staging.wanglibao.com/activity/app_ten_year/";
    var imgUrl      = "/static/imgs/mobile_activity/app_ten_year/weixin_img_300.jpg";
    var shareTitle  = "遇见10年前的你";
    var descContent = "关注网利宝，遇见10年前的你";
    var appid       = '';


    function wx_shareFriend() {
      WeixinJSBridge.invoke('sendAppMessage',{
         "appid": appid,
         "img_url": imgUrl,
         "img_width": "300",
         "img_height": "300",
         "link": lineLink,
         "desc": descContent,
         "title": shareTitle
         }, function(res) {
           //alert(res.err_msg);
         })
    }

    function wx_shareTimeline() {
      WeixinJSBridge.invoke('shareTimeline',{
        "img_url": imgUrl,
        "img_width": "300",
        "img_height": "300",
        "link": lineLink,
        "desc": descContent,
        "title": shareTitle
        }, function(res) {
           //alert(res.err_msg);
        });
    }

    function wx_shareWeibo() {
      WeixinJSBridge.invoke('shareWeibo',{
        "content": descContent,
        "url": lineLink
        }, function(res) {
          //alert(res.err_msg);
        });
    }

    function onBridgeReady(){
      WeixinJSBridge.on('menu:share:appmessage', wx_shareFriend);
      WeixinJSBridge.on('menu:share:timeline',   wx_shareTimeline);
      WeixinJSBridge.on('menu:share:weibo',      wx_shareWeibo);
    }

    if (typeof WeixinJSBridge == "undefined"){
      if( document.addEventListener ){
          document.addEventListener('WeixinJSBridgeReady', onBridgeReady, false);
      }else if (document.attachEvent){
          document.attachEvent('WeixinJSBridgeReady', onBridgeReady);
          document.attachEvent('onWeixinJSBridgeReady', onBridgeReady);
      }
    }else{
      onBridgeReady();
    }

});
