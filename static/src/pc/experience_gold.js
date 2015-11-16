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
      $('.draw_btn_ing').on('click',function(){
          $('#receiveSuccess').modal()
          $('#receiveSuccess').find('.close-modal').hide()
      })
      $('.investBtn').on('click',function(){
          $('#success').modal()
          $('#success').find('.close-modal').hide()
          setInterval(function(){
            $.modal.close()
            $('.investBtn').text('已投资8888元').addClass('invest_ed').removeClass('investBtn')
            $('.income_fonts').show()
          },2000)
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