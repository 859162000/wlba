

## 部分规范
    以下为部分文件存放规范，以下两个为示例，其他的存放规则都按照这样方式来区分。
###### images js  sass stylesheets files
    以上文件夹都为旧文件，作为过渡文件，新活动及新业务，一些资源都不往里放，特殊原因除外

######  imgs src scss styles files
    以上文件分别替代上面的旧文件
    *imgs
        imgs存放图片资源
        1.app
            为android、ios客户端webview页面图片资源存放（h5活动页的图片不放置此处）
        2.mobile
            为微信项目图片资源存放处
        3.mobile_activity
            为所有移动端活动页图片资源存放处
        4.pc
            为新版pc图片资源存放处
        5.pc_activity
            为pc段所有活动页图片资源存放处
            
    *scss        
        1.app
            为android、ios客户端webview页面样式资源存放（h5活动页的图片不放置此处)
        2.mobile    
            为微信项目样式资源存放处
        3.mobile_activity
            为所有移动端活动样式资源存放处
        4.pc
            为新版pc样式资源存放处
        5.pc_activity
            为pc段所有活动页样式资源存放处 
    
## grunt配置
###### grunt watch
    grunt compass 里的config需要根据不用项目手动修改一下
    sass  --> config.rb
    scss  --> config_weixin.rb
        

            
## include 文件
###### makrketing包 －> include
    1.app_head.jade
        该文件为app活动页所引用的头部
###### wanglibao_app －> include
    1.app_header.jade
        该文件为android\ios webview所引用的头部  
###### wanglibao －> global
    1.g_nav.jade
        该文件为pc所引用的头部导航,包括pc活动页及 新版pc页面
    2.g_footer.jade
        该文件为pc所引用的底部,包括pc活动页及 新版pc页面
    3.g_head.jade
        该文件为新版pc所引用的公用资源head里的配置,包括pc活动页及 新版pc页面
