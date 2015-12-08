(function () {
    require.config({
        paths: {
            jquery: 'lib/jquery.min'
        },
        shim: {
            'jquery.modal': ['jquery']
        }
    });

    require(['jquery'], function ($) {
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

        _getQueryStringByName = function (name) {
            var result = location.search.match(new RegExp('[\?\&]' + name + '=([^\&]+)', 'i'));
            if (result == null || result.length < 1) {
                return '';
            }
            return result[1];
        }
        //返回投票
        $('.damaifu').on('click', function () {
            $('body,html').animate({scrollTop: 957}, 600);
            return false
        })
        //dianjiquxiao
        $("input:radio").click(function () {
            var c = $(this).attr('c');
            alert(this.c);
            if (this.c == 1) {
                this.c = 0;
                this.checked = 0
            } else {
                this.c = 1
            }

        });
         $("lable").click(function () {
             if ($('lable').attr('id')) {
                 alert(12)
             }
         });

        $('.labelone').click(function () {
            if(!($(this).attr('id'))){
                $('.labelone').removeAttr('id') && $(this).attr('id', 'checked1');
                $('.labelone').prev().removeAttr('checked') && $(this).prev().attr('checked', 'checked');
            }else{
                $('.labelone').removeAttr('id')
                $('.labelone').prev().removeAttr('checked');
            }

            return false
        });
        $('.labelone1').click(function () {
            if(!($(this).attr('id'))){
                $('.labelone1').removeAttr('id') && $(this).attr('id', 'checked2');
                $('.labelone1').prev().removeAttr('checked') && $(this).prev().attr('checked', 'checked');
            }else{
                $('.labelone1').removeAttr('id')
                $('.labelone1').prev().removeAttr('checked');
            }

            return false
        });
        $('.labelone2').click(function () {
            if(!($(this).attr('id'))){
                $('.labelone2').removeAttr('id') && $(this).attr('id', 'checked');
                $('.labelone2').prev().removeAttr('checked') && $(this).prev().attr('checked', 'checked');
            }else{
                $('.labelone2').removeAttr('id')
                $('.labelone2').prev().removeAttr('checked');
            }

            return false

        });


        var point = $('.frm1'), point1 = $('.frm2'), point2 = $('.frm3');
        //if($('.frm1').checked = false){
        //    alert(123);
        //}else{
        //    alert(35)
        //}
        function piao() {
            $(this).find('.tiao').animate({
                width: '+=10px'
            }, 500);
            $(this).prev().html(parseInt($(this).prev().html()) + 1);
        }

        $('.ww').on('click', function () {

            get_radio_value(point);
            get_radio_value(point1);
            get_radio_value(point2);
            var vaq = va.substring(0, va.length - 1);
            if (vaq == '') {
                alert('请选一个')
            } else {
                alert(vaq);
            }

        })
        var va = "";

        function get_radio_value(field) {
            if (field && field.length) {

                for (var i = 0; i < field.length; i++) {
                    //alert(field[i]);
                    if (field[i].checked) {
                        va += field[i].value + ",";
                    }
                }
            } else {
                return;
            }

            //$.ajax({
            //    url: "test.html",
            //    context: document.body,
            //    data: {vaq: vaq},
            //    success: function (data) {
            //        $(this).addClass("done");
            //    }
            //});
        }

        //$('.xuan-song1').click(function () {
        //    var $radio = $(this).find("input[type=radio]"),
        //        $flag = $radio.is(":checked");
        //    if (!$flag) {
        //        $radio.prop("checked", true);
        //    }else{
        //        $radio.prop("checked", false);
        //    }
        //});


    });

})();