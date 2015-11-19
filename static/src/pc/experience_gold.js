(function() {
  require.config({
    paths: {
        jquery: 'lib/jquery.min',
        'jquery.modal': 'lib/jquery.modal.min',
        tools: 'lib/modal.tools'
    },
    shim: {
      'jquery.modal': ['jquery']
    }
  });

  require(['jquery',"tools"], function($,tool) {
      $('.no_invest').on('click',function(){
          $('#receiveSuccess').modal()
          $('#receiveSuccess').find('.close-modal').hide()
      })
      $('.invested').on('click',function(){
          $('#oldUser').modal()
          $('#oldUser').find('.close-modal').hide()
      })
      $('.investBtn').on('click',function(){
         $.ajax({
            url: '/api/experience/buy/',
            type: "POST",
            data: {}
         }).done(function (xhr) {
            $('#success').modal()
            $('#success').find('.close-modal').hide()
            setInterval(function(){
                $.modal.close()
                $('.investBtn').text('已投资'+ xhr.amount +'元').addClass('invest_ed').removeClass('investBtn')
                $('.income_fonts').show().text('将于'+ xhr.term_date +'收益'+ xhr.interest +'元')
            },2000)
         })
      })
      $('.more_btn').on('click',function(){
        $('.project_list').slideToggle()
      })
      $('#closeBtn').on('click',function(){
        $.modal.close()
      })
      $('#goBtn').on('click',function(){
        $.modal.close()
        $('body,html').animate({scrollTop: $('.experience_project').offset().top}, 600);
      })
  });
}).call(this);