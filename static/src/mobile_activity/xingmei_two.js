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
        if(data.ret_code==1003){
          $('.xm-error').text('对不起,您不符合领取规则')
        }else if(data.ret_code==0){
          $('.xm-error').text('恭喜您,您已获得奖励,请到个人用户查看')
        }else{
          $('.xm-error').text(data.message)
        }
        $('.xm-error').show()
      }
    })
  })
})();
