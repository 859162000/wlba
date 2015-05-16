module.exports = function( grunt ) {
    "use strict";
    grunt.initConfig({
        compass: {
            dist: {
                options: {
                    config: 'config_weixin.rb'
                }
            }
        },
        concat: {
            options: {
                separator: ';'
            },
            dist: {
                src: ['src/mobile/lib/zepto/zepto.js', 'src/mobile/mobile.js'],
                dest: 'scripts/mobile/mobile.js',
            }
        },
        uglify: {
            mobile: {
                files: {
                    'scripts/mobile/dist/mobile.js': ['scripts/mobile/mobile.js']
                }

            }
        }

    });

    grunt.registerTask('default', ['compass', 'concat', 'uglify']);
    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');

};


