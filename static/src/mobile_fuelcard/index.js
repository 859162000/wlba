import { Automatic } from './mixins/automatic_detection.js'


const auto = new Automatic({
                submit : $('button[type=submit]'),
                checklist: [
                    {target : $('input[name=password]'),  required:true},
                    {target : $('input[name=phone]'), required : true},
                    {target : $('input[name=validation]'), required : true},
                ],
                otherlist:[
                    {target : $('select[name=bank]'),  required:true},
                ]
                });

auto.check();
auto.operation();

$('select[name=bank]').change(function() {
    const icon = $(this).attr('data-icon');
    if($(this).val() == ''){
        $(this).siblings(`.${icon}`).removeClass('active');
    }else{
        $(this).siblings(`.${icon}`).addClass('active');
    }
   $('input[name=password]').trigger('input')
});

