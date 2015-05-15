require.config
  paths:
    jquery: 'lib/jquery.min'
    'jquery.form': 'lib/jquery.form'

  shim:
    'jquery.form': ['jquery']

require ['jquery', 'jquery.form'], ($, form)->
  $('#dete-start').val($('#selectInput').val())
  $('#dete-end').val($('#selectInput1').val())
  $('#invest-money').blur ()->
    self = $('#invest-money')
    val = $.trim(self.val())
    checkStatus = false
    if val != ''
      if val < 200
        $('.error-style').text('投标金额不能小于200')
        checkStatus = false
      else
        if parseInt(val) > parseInt($('#invest-total').val())
           $('.error-style').text('投标金额必须小于账户可用余额!')
           checkStatus = false
        else
          r = /^[1-9]\d*00(\.00|\.0)?$/
          if !r.test(val)
            $('.error-style').text('投标金额必须是 100 的倍数!')
            checkStatus = false
          else
            $('.error-style').text('')
            checkStatus = true
    else
       $('.error-style').text('请输入投标金额')
       checkStatus = false
    return checkStatus
  $('.add-ben').click ()->
    self = $('#invest-money')
    val = $.trim(self.val())
    val = 100 if val is '' or val < 100
    if parseInt(val) + 100 <= parseInt($('#invest-total').val())
      self.val(parseInt(val) + 100)
      $('.error-style').text('')
  $('.subtract').click ()->
    self = $('#invest-money')
    val = $.trim(self.val())
    if $('.error-style').text() is ''
      if parseInt(val) - 100 >= 200
        self.val(parseInt(val) - 100)
  $('.income-range').blur ()->
    self = $('#scope-min')
    val = $.trim(self.val())
    r = /^\+?[1-9]\d*$/
    if val != ''
      if !r.test(val)
        $('.error-style').text('收益范围请输入正整数')
        return false
      else if Number(val) > Number($.trim($('#scope-max').val()))
        $('.error-style').text('请填写正确收益范围')
        return false
      else
        $('.error-style').text('')
    else
      $('.error-style').text('请填写收益范围')
  $('.tender-ul-left li select').change ()->
    if Number($('#dete-start').val()) > Number($('#dete-end').val())
      $('.error-style').text('请选择正确收益期限')
      return false
    else
       $('.error-style').text('')
  $('#submit').click ()->
    $('#invest-money').blur()
    if $('.error-style').text() is ''
       $('.income-range').blur()
    if Number($('#dete-start').val()) > Number($('#dete-end').val())
      $('.error-style').text('请选择正确收益期限')
      return false
    if $('.error-style').text() is ''
      $('#tenderForm').ajaxSubmit (data) ->
        $('.error-style').text(data.message)
