//(function(a,h,c,b,f,g){a["UdeskApiObject"]=f;a[f]=a[f]||function(){(a[f].d=a[f].d||[]).push(arguments)};g=h.createElement(c);g.async=1;g.src=b;c=h.getElementsByTagName(c)[0];c.parentNode.insertBefore(g,c)})(window,document,"script","https://18612250386.udesk.cn/im_client/js/udeskApi.js?_t=1464168984272","ud"); ud({"code":"h3g84ai","link":"https://18612250386.udesk.cn/im_client","isInvite":true,"mobile":{"mode":"blank","color":"#307AE8","pos_flag":"crb","onlineText":"联系客服，在线咨询","offlineText":"客服下班，请留言","pop":{"direction":"top","arrow":{"top":0,"left":"70%"}}},"mode":"blank","color":"#307AE8","pos_flag":"srb","onlineText":"联系客服，在线咨询","offlineText":"客服下班，请留言","pop":{"direction":"top","arrow":{"top":0,"left":"80%"}}});

 (function() {
    require.config({
        paths: {
            jquery: 'lib/jquery.min'
        },
        shim: {
            'jquery.modal': ['jquery']
        }
    });
    require(['jquery'],
    function($, re) {

        var csrfSafeMethod, getCookie, sameOrigin,
            getCookie = function (name) {
                var cookie, cookieValue, cookies, i;
                cookieValue = null;
                if (document.cookie && document.cookie !== "") {
                    cookies = document.cookie.split(";");
                    i = 0;
                    while (i < cookies.length) {
                        cookie = $.trim(cookies[i]);
                        if (cookie.substring(0, name.length + 1) === (name + "=")) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                        i++;
                    }
                }
                return cookieValue;
            };
        csrfSafeMethod = function (method) {
            return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
        };
        sameOrigin = function (url) {
            var host, origin, protocol, sr_origin;
            host = document.location.host;
            protocol = document.location.protocol;
            sr_origin = "//" + host;
            origin = protocol + sr_origin;
            return (url === origin || url.slice(0, origin.length + 1) === origin + "/") || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + "/") || !(/^(\/\/|http:|https:).*/.test(url));
        };
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
                }
            }
        });

        function footer_js(){


        var openUrl = "http://wanglibao.udesk.cn/im_client/";//弹出窗口的url
        var iWidth = 780; //弹出窗口的宽度;
        var iHeight = 615; //弹出窗口的高度;
        var iTop = 225; //获得窗口的垂直位置;
        var iLeft = 400; //获得窗口的水平位置;

        var url_search = window.location.search,openKefu='';
        var searchArray = url_search.substring(1).split("?");
        for(var i = 0;i < searchArray.length; i++){
            var temp = searchArray[i].split('=');
            if(temp[0] == 'openKefu'){
                openKefu = temp[1] ? temp[1] : '';
            }
        }

        var user_login_status = false;
        $.ajax({
            url: '/api/user_login/',
            type: 'post',
            success: function(data1) {
                user_login_status = data1.login;
                if(openKefu==1&&user_login_status==true){
                    location.hash="#kefu_link";
                }
            }
        });

        //alert(openKefu);

        $('#kefu_link').click(function(){
            if(user_login_status){
                var newWin = window.open('',"_blank", "height=" + iHeight + ", width=" + iWidth + ", top=" + iTop + ", left=" + iLeft);
            }

          $.ajax({
            url: '/api/udesk/url/',
            type: 'post',
            data:{

            },
            success: function (data) {
                if(data.ret_code=='1000'||data.ret_code=='1001'){
                    $('.popup_box .main .textairport').text(data.message);
                    $('.popup_box').show();

                }else if(data.ret_code=='0'){
                    openUrl = data.url;
                    //弹出窗口的url
                    newWin.location.href = openUrl;
                }

            },error: function(data){
                $('.popup_box .main .textairport').text('系统繁忙，请稍后再试');
                $('.popup_box').show();
            }
          })
        })


        $('.popup_box .popup_button').click(function(){

            var this_link = window.location.href;
            var this_link_1 = this_link.indexOf("/accounts/login/");
            var this_link_2 = this_link.indexOf("/accounts/register/");
            var this_link_indexof = window.location.href.indexOf("?");
            if(this_link_1==-1&&this_link_2==-1){

                if(openKefu!=1&&user_login_status==false){
                    if(this_link_indexof!=-1){
                        var go_link = window.location.href+'&openKefu=1';
                    }else{
                        var go_link = window.location.href+'?openKefu=1';
                    }

                    window.location.href = '/accounts/login/?next='+go_link+'';
                }
            }else{
                $('.popup_box').hide();
            }

        });
    }
    footer_js();

    })
}).call(this);