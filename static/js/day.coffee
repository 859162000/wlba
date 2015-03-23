require.config(
  paths:
    jquery: 'lib/jquery.min'
)

require ['jquery'], ($)->

#  倒计时
  count_down = (o) ->
    sec=(new Date(o.replace(/-/ig,'/')).getTime() - new Date().getTime())/1000
    sec=parseInt(sec)
    timer=setTimeout (->
      count_down o
      return
    ), 1000
    if sec <=0
      $('.mon').html('4 月')
      $('.day-long').animate({'left':'-357px'},500)
      hight(m,'.day-si')
      clearTimeout(timer)
      count_down('2015-04-31 24:00:00')
    return



#  high_day=parseInt()
  hight=(high_m,ele)->
    g=0
    while g<$('.day-yue li').length-2
      k=0
      while k<$(ele+' li:eq('+g+')').children('span').length

        if m==high_m and day==parseInt($(ele+' li:eq('+g+')').children('span:eq('+k+')').text())

          $(ele+' li:eq('+g+')').children('span:eq('+k+')').addClass('tap-hight2').siblings().removeClass('tap-hight2')
#          $('.day-san').children('span').removeClass('tap-hight2')
          $(ele+' li:eq('+g+')').children('span:eq('+k+')').css({'background':'rgb(244, 136, 144)','color':'#000'})
        k++
      g++

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
    $.ajax {
      url: '/activity/investment_history/'
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
      if day.length<2
          day='0'+day
      date=Y+'-0'+m+"-"+day
      j=0
      str='<li class="day-user-hight"><span>榜单</span><span>用户</span><span>投标金额</span></li>'
      str2='<li class="day-user-hight"><span>榜单</span><span>用户</span><span>投标金额</span></li>'
      str3='<li class="day-user-hight"><span>榜单</span><span>用户</span><span>投标金额</span></li>'
      str4='<li class="day-user-hight"><span>榜单</span><span>用户</span><span>投标金额</span></li>'
      str5='<li class="day-user-hight"><span>榜单</span><span>用户</span><span>投标金额</span></li>'
      if date!=time
        while j<10
          if data[0]['tops_len']==0
  #          console.log(date)
            console.log(time)
            if j%2==0
              str3+='<li><span class="day-user-hight2">'+(j+1)+'</span><span>－－</span><span>－－</span></li>'
              $('#dan').html(str3)
            if j%2!=0
              str4+='<li><span class="day-user-hight2">'+(j+1)+'</span><span>－－</span><span>－－</span></li>'
              $('#shuang').html(str4)
          if data[0]['tops_len']!=0
            if data[0]['tops_len']==1
              if j%2==0
                if j< data[0]['tops_len']
                  str+='<li><span class="day-user-hight2">'+(j+1)+'</span><span>'+data[0]['tops'][j]['phone']+'</span><span>'+fmoney(data[0]['tops'][j]['amount_sum'])+' 元</span></li>'
                  $('#dan').html(str)
                if j>data[0]['tops_len']
                  str3='<li><span class="day-user-hight2">'+(j+1)+'</span><span>－－</span><span>－－</span></li>'
                  $('#dan').append(str3)
              if j%2!=0
                str5+='<li><span class="day-user-hight2">'+(j+1)+'</span><span>－－</span><span>－－</span></li>'
                $('#shuang').html(str5)
            else
              if j%2==0
                if j< data[0]['tops_len']
                  str+='<li><span class="day-user-hight2">'+(j+1)+'</span><span>'+data[0]['tops'][j]['phone']+'</span><span>'+fmoney(data[0]['tops'][j]['amount_sum'])+' 元</span></li>'
                  $('#dan').html(str)
                if j>=data[0]['tops_len']
                  str3='<li><span class="day-user-hight2">'+(j+1)+'</span><span>－－</span><span>－－</span></li>'
                  $('#dan').append(str3)
              if j%2!=0
                if j<data[0]['tops_len']
                  str2+='<li><span class="day-user-hight2">'+(j+1)+'</span><span>'+data[0]['tops'][j]['phone']+'</span><span>'+fmoney(data[0]['tops'][j]['amount_sum'])+' 元</span></li>'
                  $('#shuang').html(str2)
                if j>=data[0]['tops_len']
                  str3='<li><span class="day-user-hight2">'+(j+1)+'</span><span>－－</span><span>－－</span></li>'
                  $('#shuang').append(str3)
          j++
      else
        while j<10
          if data[0]['tops_len']==0
            if j%2==0
              str3+='<li><span class="day-user-hight2">'+(j+1)+'</span><span>虚位以待</span><span>虚位以待</span></li>'
              $('#dan').html(str3)
            if j%2!=0
              str4+='<li><span class="day-user-hight2">'+(j+1)+'</span><span>虚位以待</span><span>虚位以待</span></li>'
              $('#shuang').html(str4)
          if data[0]['tops_len']!=0
            if data[0]['tops_len']==1
              if j%2==0
                if j< data[0]['tops_len']
                  str+='<li><span class="day-user-hight2">'+(j+1)+'</span><span>'+data[0]['tops'][j]['phone']+'</span><span>'+fmoney(data[0]['tops'][j]['amount_sum'])+' 元</span></li>'
                  $('#dan').html(str)
                if j>data[0]['tops_len']
                  str3='<li><span class="day-user-hight2">'+(j+1)+'</span><span>虚位以待</span><span>虚位以待</span></li>'
                  $('#dan').append(str3)
              if j%2!=0
                str5+='<li><span class="day-user-hight2">'+(j+1)+'</span><span>虚位以待</span><span>虚位以待</span></li>'
                $('#shuang').html(str5)
            else
              if j%2==0
                if j< data[0]['tops_len']
                  str+='<li><span class="day-user-hight2">'+(j+1)+'</span><span>'+data[0]['tops'][j]['phone']+'</span><span>'+fmoney(data[0]['tops'][j]['amount_sum'])+' 元</span></li>'
                  $('#dan').html(str)
                if j>=data[0]['tops_len']
                  str3='<li><span class="day-user-hight2">'+(j+1)+'</span><span>虚位以待</span><span>虚位以待</span></li>'
                  $('#dan').append(str3)
              if j%2!=0
                if j<data[0]['tops_len']
                  str2+='<li><span class="day-user-hight2">'+(j+1)+'</span><span>'+data[0]['tops'][j]['phone']+'</span><span>'+fmoney(data[0]['tops'][j]['amount_sum'])+' 元</span></li>'
                  $('#shuang').html(str2)
                if j>=data[0]['tops_len']
                  str3='<li><span class="day-user-hight2">'+(j+1)+'</span><span>虚位以待</span><span>虚位以待</span></li>'
                  $('#shuang').append(str3)
          j++
# 获取当天日期
  data=new Date()
  Y=data.getFullYear()
  m=data.getMonth()+1
  day=data.getDate()
  if day.length<2
      day='0'+day
  date=Y+'-0'+m+"-"+day
  hight(m,'.day-san')
  shuju(date)
  $('#left-h1').html('－－'+m+'月'+day+'日用户榜单－－')

#获取倒计时时间

  count_down('2015-04-01 00:00:00')
#  tap切换
  $('.left-btn').on('click',()->
    $('.mon').html('3 月')
    $('.day-long').animate({'left':'0px'},500)
    $('.day-si span').removeClass('tap-hight2')
    high_m=parseInt($('.mon').text())
    hight(high_m,'.day-san')
  )
  $('.right-btn').on('click',()->
    $('.mon').html('4 月')
    $('.day-long').animate({'left':'-357px'},500)
    $('.day-san span').removeClass('tap-hight2')
    high_m=parseInt($('.mon').text())
    hight(high_m,'.day-si')
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
    m=data.getMonth()+1
    day=data.getDate()
    date=Y+'-0'+m+"-"+day
    if time>='2015-03-17' and time<='2015-04-30' and time<=date
      $(this).addClass('tap-hight2').siblings().removeClass('tap-hight2')
      $(this).parent().siblings().children('span').removeClass('tap-hight2')
      $('#left-h1').html('－－'+m+'月'+d+'日用户榜单－－')
      shuju(time)
  )





