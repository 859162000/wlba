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

    require(['jquery', "tools"], function($, tool) {
        $('#showRule').on('click',function(){
            $('#showRuleDetail').modal({
                modalClass: 'alert-box-c',
                closeClass: 'close-btn'
            })
        })
    });
}).call(this);