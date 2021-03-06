require.config(
  paths:
    jquery: 'lib/jquery.min'
)

require ['jquery'], ($)->
#  缓存
  init = (time)->
    csrfSafeMethod = undefined
    getCookie = undefined
    sameOrigin = undefined

    getCookie = (name) ->
      cookie = undefined
      cookieValue = undefined
      cookies = undefined
      i = undefined
      cookieValue = null
      if document.cookie and document.cookie != ''
        cookies = document.cookie.split(';')
        i = 0
        while i < cookies.length
          cookie = $.trim(cookies[i])
          if cookie.substring(0, name.length + 1) == name + '='
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
            break
          i++
      cookieValue

    csrfSafeMethod = (method) ->
      /^(GET|HEAD|OPTIONS|TRACE)$/.test method

    sameOrigin = (url) ->
      host = undefined
      origin = undefined
      protocol = undefined
      sr_origin = undefined
      host = document.location.host
      protocol = document.location.protocol
      sr_origin = '//' + host
      origin = protocol + sr_origin
      url == origin or url.slice(0, origin.length + 1) == origin + '/' or url == sr_origin or url.slice(0, sr_origin.length + 1) == sr_origin + '/' or !/^(\/\/|http:|https:).*/.test(url)

    $.ajaxSetup beforeSend: (xhr, settings) ->
      if !csrfSafeMethod(settings.type) and sameOrigin(settings.url)
        xhr.setRequestHeader 'X-CSRFToken', getCookie('csrftoken')
      return
    shuju(time)
    return

#  倒计时
#  count_down = (o) ->
#    sec=(new Date(o.replace(/-/ig,'/')).getTime() - new Date().getTime())/1000
#    sec=parseInt(sec)
#    timer=setTimeout (->
#      count_down o
#      return
#    ), 1000
#    if sec <=0
#      $('.mon').html('5 月')
#      $('.day-long').animate({'left':'-714px'},500)
#      #hight(m,'.day-wu')
#      clearTimeout(timer)
#      day_index=2;
#    return



#  high_day=parseInt()
#  hight=(high_m,ele)->
#    data=new Date()
#    Y=data.getFullYear()
#    m=data.getMonth()+1
#    day=data.getDate()
#    if m==6 and day>10
#      return
#    g=0
#    while g<$('.day-yue li').length-2
#      k=0
#      while k<$(ele+' li:eq('+g+')').children('span').length
#        if m==high_m and day==parseInt($(ele+' li:eq('+g+')').children('span:eq('+k+')').text())
#          $(ele+' li:eq('+g+')').children('span:eq('+k+')').addClass('span-high').siblings().removeClass('span-high')
#          $('.day-wu').children('span').removeClass('span-high')
#          $(ele+' li:eq('+g+')').children('span:eq('+k+')').css({'background':'url("/static/images/list-img/small.png") no-repeat','background-position':'-187px -86px','color':'#000'})
#        if m!=high_m and day==parseInt($(ele+' li:eq('+g+')').children('span:eq('+k+')').text())
#          $(ele+' li:eq('+g+')').children('span:eq('+k+')').css({'background':'#FFB7C5','color':'#666671','font-weight':'normal'})
#        k++
#      g++

#  格式化金额
  fmoney = (s, n) ->
    n = if n > 0 and n <= 20 then n else 2
    s = parseFloat((s + '').replace(/[^\d\.-]/g, '')).toFixed(n) + ''
    l = s.split('.')[0].split('').reverse()
    r = s.split('.')[1]
    t = ''
    i = 0
    while i < l.length
      t += l[i] + (if (i + 1) % 3 == 0 and i + 1 != l.length then ',' else '')
      i++
    t.split('').reverse().join('')
  #  请求数据
  shuju=(time)->
    $("#dan li").not(":first").remove()
    $.ajax {
      url: '/api/investment_history/'
      data: {
        day: time
      }
      type: 'POST'
    }
    .done (data)->
      data=JSON.parse(data)
      date=new Date()
      Y=date.getFullYear()
      m=date.getMonth()+1
      day=date.getDate()

      if day<10
          day='0'+day
      date=Y+'-0'+m+"-"+day
      j=0
      str=''
      if date!=time
        while j<10
          if data[0]['tops_len']==0
            str+='<li class="color9"><span class="span-one"></span><span class="span-two">－－</span><span class="span-three">－－</span></li>'
          if data[0]['tops_len']!=0
            if data[0]['tops_len']==1
              if j< data[0]['tops_len']
                str+='<li><span class="span-one"></span><span class="span-two">'+data[0]['tops'][j]['phone']+'</span><span class="span-three">'+fmoney(data[0]['tops'][j]['amount_sum'])+' 元</span></li>'
              else
                str+='<li class="color9"><span class="span-one"></span><span class="span-two">－－</span><span class="span-three">－－</span></li>'
            else
              if j< data[0]['tops_len']
                str+='<li><span class="span-one"></span><span class="span-two">'+data[0]['tops'][j]['phone']+'</span><span class="span-three">'+fmoney(data[0]['tops'][j]['amount_sum'])+' 元</span></li>'
              else
                str+='<li class="color9"><span class="span-one"></span><span class="span-two">－－</span><span class="span-three">－－</span></li>'
          j++

      else
        while j<10
          if data[0]['tops_len']==0
            str+='<li class="color6"><span class="span-one"></span><span class="span-two">虚位以待</span><span class="span-three">虚位以待</span></li>'
          if data[0]['tops_len']!=0
            if data[0]['tops_len']==1
              if j< data[0]['tops_len']
                str+='<li><span class="span-one"></span><span class="span-two">'+data[0]['tops'][j]['phone']+'</span><span class="span-three">'+fmoney(data[0]['tops'][j]['amount_sum'])+' 元</span></li>'
              else
                str+='<li class="color6"><span class="span-one"></span><span class="span-two">虚位以待</span><span class="span-three">虚位以待</span></li>'
            else
              if j< data[0]['tops_len']
                str+='<li><span class="span-one"></span><span class="span-two">'+data[0]['tops'][j]['phone']+'</span><span class="span-three">'+fmoney(data[0]['tops'][j]['amount_sum'])+' 元</span></li>'
              else
                str+='<li class="color6"><span class="span-one"></span><span class="span-two">虚位以待</span><span class="span-three">虚位以待</span></li>'
          j++
      if str != ''
        $('#dan').html('<li class="day-user-hight"><span class="span-one">榜单</span><span class="span-two">用户</span><span class="span-three">投标金额</span></li>')
        $('#dan').append(str)

# 获取当天日期
  data=new Date()
  Y=data.getFullYear()
  m=data.getMonth()+1
  day=data.getDate()
  if day<10
      day='0'+day
  date=Y+'-0'+m+"-"+day
  #hight(m,'day-wu')   .addClass('span-high')
  selectSpanFun(m,day)
  day_index = m - 3

  init(date)
  $('#left-h1').html(+m+'月'+day+'日用户榜单')
  wei=new Date()
  wei2=new Date()
  wei2.setMonth(2)
  wei2.setDate(24)
  wei2.setHours(0)
  wei2.setMinutes(0)
  wei2.setSeconds(0)
  gotime=wei2.getTime()-wei.getTime()

  setTimeout(()->
    $('.ing li').eq(1).addClass('ing-hight')
    $('.day-head h1').eq(1).addClass('h1-hight')
  gotime)

#获取倒计时时间
#  if m==6
#    sec=(new Date('2015-06-01'.replace(/-/ig,'/')).getTime() - new Date().getTime())/1000
#    sec=parseInt(sec)
#    timer=setTimeout (->
#      count_down '2015-06-01'
#      return
#    ), 1000
#    if sec <=0
#      $('.mon').html('6 月')
#      $('.day-long').animate({'left':'-1107px'},500)
#      #hight(m,'.day-liu')
#      #selectSpanFun(m,day)
#      clearTimeout(timer)
#      day_index=3;
#  else
#    count_down('2015-05-01 0:0:0')


#  tap切换
#  $('.left-btn').on('click',()->
#    $('.mon').html('3 月')
#    $('.day-long').animate({'left':'0px'},500)
#    $('.day-si span').removeClass('tap-hight2')
#    high_m=parseInt($('.mon').text())
#    hight(high_m,'.day-san')
#
#  )
#  $('.right-btn').on('click',()->
#    $('.mon').html('4 月')
##    $('.day-long').animate({'left':'-357px'},500)
#    $('.day-san span').removeClass('tap-hight2')
#
#    while
#      $('.day-long').animate({'left':-357*day_index+'px'},500)
#      day_index++;
#    high_m=parseInt($('.mon').text())
#    hight(high_m,'.day-si')
#  )
  mon=0;
  $('.right-btn').on('click',()->
      day_index++;
      if day_index<$('.day-yue').length
        mon=day_index+3
        $('.mon').html(mon+' 月')
        $('.day-long').animate({'left':-369*day_index+'px'},500)
#        high_m=parseInt($('.mon').text())
#        high_num=$('.day-yue:eq('+day_index+')').attr('data-num')
#        hight(high_m,high_num)
      else
        day_index=6
#        $('.day-long').animate({'left':'0px'},500)
#        $('.mon').html(3+' 月')
  )

  $('.left-btn').on('click',()->
      day_index--;
      if day_index>=0
        mon=day_index+3
        $('.mon').html(mon+' 月')
        $('.day-long').animate({'left':-369*day_index+'px'},500)
#        high_m=parseInt($('.mon').text())
#        high_num=$('.day-yue:eq('+day_index+')').attr('data-num')
#        hight(high_m,high_num)
      else
        day_index=0
  )

#  获取年月日
  $('.day-yue span').on('click',()->
    m=parseInt($('.mon').text())
    d=$(this).text()
    if d.length<2
      d='0'+d
    time='2015-0'+m+'-'+d
    data=new Date()
    Y=data.getFullYear()
    zm=data.getMonth()+1
    day=data.getDate()
    if day<10
      day='0'+day
    date=Y+'-0'+zm+"-"+day
    if time>='2015-06-14' and time<='2015-07-15' and time<=date
      $(this).addClass('tap-hight2').siblings().removeClass('tap-hight2')
      $(this).parent().siblings().children('span').removeClass('tap-hight2')
      $('#left-h1').html(+m+'月'+d+'日用户榜单')
      shuju(time)
  )
  $('.day-list').on('click',()->
    if !$('.day-list').hasClass('curr')
      $('.day-list').addClass('curr')
      $('.day-list-div').show()
      $('.history-list-div').hide()
      $('.history-list').removeClass('curr')
  )
  $('.history-list').on('click',()->
    if !$('.history-list').hasClass('curr')
      $('.history-list').addClass('curr')
      $('.history-list-div').show()
      $('.day-list-div').hide()
      $('.day-list').removeClass('curr')
  )



