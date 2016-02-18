/**
 * Created by rsj217 on 16-2-18.
 */

(function(){
  //$('.no-reg').on('click',function(){
  //  $('.xm-error').show()
  //
  //})
  $('.no-reg').on('click',function(){
    org.ajax({
      type: 'POST',
      data: {activity:'xm2'},
      url: '/api/activity/reward/',
      success: function(data){
        $('.xm-error').text(data.message)
        $('.xm-error').show()
      }
    })
  })
})();
