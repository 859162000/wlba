require.config
  paths:
    jquery: 'lib/jquery.min'
    tools: 'lib/modal.tools'
    "jquery.validate": 'lib/jquery.validate.min'
    'jquery.modal': 'lib/jquery.modal.min'

  shims:
    "jquery.modal": ["jquery"]
    "tools": ['jquery.modal']


require ['jquery', 'tools'], ($, tool)->


  $('.exchange').click (e) ->
    e.preventDefault()
    token = $.trim($('input[name="token"]').val())
    if token != ''
      $.post('/api/redpacket/exchange/'
        token: token
      ).done( (data) ->
        if data.ret_code == 0
          tool.modalAlert({btnText:"确认", title: '温馨提示', msg: '兑换成功', callback_ok: ()->
            window.location.reload()
          })

        else
          tool.modalAlert({btnText:"确认", title: '温馨提示', msg: data.message})
      ).fail (data)->
        tool.modalAlert({btnText:"确认", title: '温馨提示', msg: '服务器忙，请稍后重试'})

    else
      tool.modalAlert({btnText:"确认", title: '温馨提示', msg: '兑换码不能为空'})



