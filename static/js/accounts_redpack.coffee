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

  console.log('hello')

  $('.exchange').click (e) ->
    e.preventDefault()
    console.log('nothing')
    if $.trim($('input[name="token"]').val()) != ''
      $.post('/api/redpacket/exchange/'
        token: '9MP4DFUM'
      ).done (data) ->
        console.log(data)
        if data.ret_code == 0
          tool.modalAlert({btnText:"确认", title: '温馨提示', msg: '兑换成功', callback_ok: ()->
            window.location.reload()
          })

        else
          tool.modalAlert({btnText:"确认", title: '温馨提示', msg: data.message})

    else
      console.log('hello')



