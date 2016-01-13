require(['jquery'], function( $ ) {
    var checkUserStatus = function(type){
        $.ajax({
          url: '/qiye/profile/exists/',
          type: "GET",
          data: {
          }
        }).done(function(data) {
            if(data.ret_code == 10000){
                $.ajax({
                  url: '/qiye/profile/get/',
                  type: "GET",
                  data: {
                  }
                }).done(function(data) {
                    if(data.data.status == '审核通过'){
                         $('#checkUserType').attr('href','/accounts/home/')
                    }else{
                        $('#checkUserType').attr('href','/qiye/profile/edit/');
                        if(type != '1'){
                            $('#minNavs').hide()
                        }
                    }
                })
            }
        }).fail(function(data){
            var result = JSON.parse(data.responseText);
            if(result.ret_code == 20001){
                if(type == '1'){
                    window.location.href = '/qiye/register/'
                }else{
                    $('#checkUserType').attr('href','/accounts/home')
                }
            }else{
               $('#checkUserType').attr('href','/qiye/info/');
               if(type != '1') {
                   $('#minNavs').hide()
               }else{
                   window.location.href = '/qiye/info/'
               }
            }
        })
    }
    $('#investment').on('click',function(){
        if($('.checkLoginStatus').length > 0){
            checkUserStatus('1');
        }else{
            window.location.href = '/qiye/register/'
        }
    })

     checkUserStatus('2');
})