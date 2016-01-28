/**
 * Created by zzl on 16-1-25.
 */
(function(){
    require.config({
        paths: {
            jquery: 'lib/jquery.min'
        },
        shim: {
            'jquery.modal': ['jquery']
        }
    });
    require(["jquery"],function($){
        var csrfSafeMethod, getCookie, sameOrigin;
        getCookie = function(name) {
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
        csrfSafeMethod = function(method) {
          return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
        };
        sameOrigin = function(url) {
          var host, origin, protocol, sr_origin;
          host = document.location.host;
          protocol = document.location.protocol;
          sr_origin = "//" + host;
          origin = protocol + sr_origin;
          return (url === origin || url.slice(0, origin.length + 1) === origin + "/") || (url === sr_origin || url.slice(0, sr_origin.length + 1) === sr_origin + "/") || !(/^(\/\/|http:|https:).*/.test(url));
        };
        $.ajaxSetup({
          beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
              xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
            }
          }
        });
        $(".years_pot_minbox").on("click",function(){
            var data = $(this).attr("data");
            isdata(data)
            ajaxfn(null, "/api/wlb_reward/qm_banque/", function(data){
                var txt=data.message;
                if(data.ret_code == 0) {
                    $.each(data.redpack_txts,function(idx,val){
                        var text="<li>"+val+"</li>";
                        $(".years_smkal").show().find("ul").append(text);
                    })
                }else{
                    $('.years_smak').show().find("h3").text(txt);
                }
            })
            $(".cover_layer").show();
        })
        function ajaxfn(id, url, fn){
            $.ajax({
                type: "post",
                url: url,
                data: {redpack_id : id},
                success: function(data){
                    fn(data)
                }
            })
        }
        $(".years_paper a").on("click",function(){
            var data_id=$(this).attr("data_id");
            ajaxfn(data_id, "/api/wlb_reward/hm_banque/#", function(data){
                var txt=data.message;
                if(data.ret_code == 0){
                    $('.years_smak').show();

                }else{
                    $('.years_smak').show().find("h3").text(txt);
                }
            })
            $(".cover_layer").show();
        })
        $(".years_close").on("click",function(){
            $(this).parent().parent().hide();
            $(".cover_layer").hide();
        })
        isdata = function(data){
            if(data == 2){
                $("#boil").animate({"left" : 16+"%", "top" : 80+"px"},500);
            }else if(data == 3){
                $("#boil").animate({"left" : 84+"%", "top" : 80+"px"},500);
            }else if(data == 4){
                $("#boil").animate({"left" : 49.5+"%", "top" : 244+"px"},500);
            }else{
                $("#boil").animate({"left" : 50+"%", "top" : -85+"px"},500);
            }
        }
        $(".years_explain_box").hide();
        $("#years_gui").on('click',function(){
            $(".years_explain_box").slideToggle(500);
        })

    })
})()