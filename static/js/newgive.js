(function() {
  require.config({
    paths: {
      jquery: 'lib/jquery.min',
      'jquery.modal': 'lib/jquery.modal.min',
      'activityRegister': 'activityRegister'
    },
    shim: {
      'jquery.modal': ['jquery']
    }
  });

  require(['jquery','activityRegister'], function($,re) {
    //注册
    re.activityRegister.activityRegisterInit({
        registerTitle :'领取迅雷会员+现金红包',    //注册框标语
        isNOShow : '0',
        buttonFont: '立即注册'
    });

  });
}).call(this);
