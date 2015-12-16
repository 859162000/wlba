import { Automatic } from './mixins/automatic_detection.js'


const auto = new Automatic({
                submit : $('button[type=submit]'),
                checklist: [
                    {target : $('input[name=username]'),  required:true},
                    {target : $('input[name=idcard]'), required : true},
                ]
                });

auto.check();

