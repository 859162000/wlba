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
      $('.draw_btn_ed').on('click',function(){
          $('#receiveSuccess').modal()
      })
  });
}).call(this);