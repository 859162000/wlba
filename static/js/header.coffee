require.config
  paths:
    jquery: 'lib/jquery.min'
    iealert: 'lib/iealert.min'
  shim:
    'iealert': ['jquery']

require ['jquery', 'lib/backend', 'iealert'], ($, backend, iealert)->
  $(document).ready ()->
    $("body").iealert({
      title: "您使用的IE浏览器版本过低",
      text: '为了获得更好的浏览体验，请点击下面的按钮升级您的浏览器',
      upgradeTitle: '立即升级',
      support: 'ie7',
      closeBtn: false
    })
