require.config({
    paths: {
        'jquery.placeholder': 'lib/jquery.placeholder',
        'jquery.form': 'lib/jquery.form',
        'jquery.validate': 'lib/jquery.validate',
        'jquery.modal': 'lib/jquery.modal.min',
        'jquery.webuploader': 'lib/webuploader.min',
        tools: 'lib/modal.tools',
        upload: 'upload',
        'csrf' : 'model/csrf',
        'code' : 'model/sendCode'
    },
    shim: {
        'jquery.placeholder': ['jquery'],
        'jquery.form': ['jquery'],
        'jquery.validate': ['jquery'],
        'jquery.modal': ['jquery'],
        'jquery.webuploader': ['jquery']
    }
});

require(['jquery', 'jquery.form', 'jquery.validate', 'jquery.placeholder', 'lib/modal', 'tools', 'jquery.webuploader' ,'code', 'upload', 'csrf'], function ($, form ,validate, placeholder, modal, tool, webuploader, code) {

    code.sendSMSCode.sendSMSCodeInit({
        sendCodeBtn :'button-get-code-btn'
    })

    code.sendSMSCode.sendSMSCodeInit({
        sendCodeBtn :'button-get-code-btn1'
    })

    //提交表单
    var qiyeFormValidate = $('#qiyeForm').validate({});
    $('.save-btn').on('click',function(){
        if(qiyeFormValidate.form()){
            $('#qiyeForm').ajaxSubmit(function(data){

            })
        }
    })

   $('#yezz').diyUpload({
        url:'server/fileupload.php',
        success:function( data ) {
            console.info( data );
        },
        error:function( err ) {
            console.info( err );
        },
        buttonText : '营业执照',
        chunked:true,
        // 分片大小
        chunkSize:512 * 1024,
        //最大上传的文件数量, 总文件大小,单个文件大小(单位字节);
        fileNumLimit:1,
        fileSizeLimit:500000 * 1024,
        fileSingleSizeLimit:50000 * 1024,
        accept: {}
    });
    $('#swdjz').diyUpload({
        url:'server/fileupload.php',
        success:function( data ) {
            console.info( data );
        },
        error:function( err ) {
            console.info( err );
        },
        buttonText : '登记证',
        chunked:true,
        // 分片大小
        chunkSize:512 * 1024,
        //最大上传的文件数量, 总文件大小,单个文件大小(单位字节);
        fileNumLimit:1,
        fileSizeLimit:500000 * 1024,
        fileSingleSizeLimit:50000 * 1024,
        accept: {}
    });
    //输入框
    $('input, textarea').placeholder();
});
