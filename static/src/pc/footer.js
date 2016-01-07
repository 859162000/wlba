require(['jquery'], function( $ ) {
    _getQueryStringByName = function(name){
            var result = location.search.match(new RegExp('[\?\&]' + name+ '=([^\&]+)','i'));
             if(result == null || result.length < 1){
                 return '';
             }
             return result[1];
    }
    $('#investment').on('click',function(){
        if($('.checkLoginStatus').length > 0){
            $.ajax({
              url: '/qiye/profile/exists/',
              type: "GET",
              data: {
              }
            }).done(function(data) {
                if(data.ret_code == 10000){
                    window.location.href = '/accounts/home/';
                }
            }).fail(function(data){
                var result = JSON.parse(data.responseText);
                if(result.ret_code == 20001){
                    window.location.href = '/qiye/register/'
                }else{
                    window.location.href = '/qiye/info/';
                }
            })
        }else{
            window.location.href = '/qiye/register/'
        }
    })
})