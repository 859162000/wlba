require.config(
  paths:
    jquery: 'lib/jquery.min'
)

require ['jquery'], ($)->
  $('#btn_sub').click (e) ->
    phone = $('#phone').val()
    title = $('#title').val()
    content = $('#content').val()
    mtype = $('#mtype').val()
    $.ajax
      url: '/api/admin_send_message/'
      data: {
        phone: phone
        title: title
        content: content
        mtype: mtype
      }
      type: 'post'
      dataType: "json",
    .done (xhr)->
      alert(xhr.message)
      $("#phone").val("")
      $("#title").val("")
      $("#content").val("")
    .fail (xhr)->
      alert("服务器异常")
