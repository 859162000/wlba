require(['jquery'], function( $ ) {
    $.ajax({
      url: '/qiye/profile/exists/',
      type: "GET",
      data: {
      }
    }).done(function(data) {
        if(data.ret_code == 10000){
            $('.finishEd').show()
        }
    }).fail(function(data){
        $('.finishing').show()
        $('.g-user-warp').hide()
    })
})