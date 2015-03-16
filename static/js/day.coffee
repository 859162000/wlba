require.config(
  paths:
    jquery: 'lib/jquery.min'
)

require ['jquery'], ($)->
#  tap切换
  $('.left-btn').on('click',()->
    $('.mon').html('3 月')
    $('.day-long').animate({'left':'0px'},500)
    $('.day-si span').removeClass('tap-hight2')
  )
  $('.right-btn').on('click',()->
    $('.mon').html('4 月')
    $('.day-long').animate({'left':'-357px'},500)
    $('.day-san span').removeClass('tap-hight2')
  )

#  获取年月日
  $('.day-yue span').on('click',()->
    m=parseInt($('.mon').text())
    d=$(this).text()
    $(this).addClass('tap-hight2').siblings().removeClass('tap-hight2')
    $(this).parent().siblings().children('span').removeClass('tap-hight2')
    $('.left-h1').html('－－'+m+'月'+d+'日用户榜单－－')
    if d.length<2
      d='0'+d
    time='2015-0'+m+'-'+d
    shuju(time)
  )

#  请求数据
  shuju=(time)->
    $.ajax {
      url: '/activity/investment_history/'
      data: {
        day: time
      }
      type: 'GET'
    }
    .done (data)->
      alert(data)