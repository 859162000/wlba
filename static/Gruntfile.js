module.exports = function( grunt ) {
    "use strict";

    //var mozjpeg = require('imagemin-mozjpeg');

    grunt.initConfig({
        compass: {
            dist: {
                options: {
                    config: 'config.rb'
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
                files: [
                    {
                        expand: true,
                        cwd: 'scripts/mobile_activity/',
                        src: '*.js',
                        dest: 'scripts/mobile_activity/dist/'
                    },
                    {
                        expand: true,
                        cwd: 'scripts/mobile/',
                        src: '*.js',
                        dest: 'scripts/mobile/dist/'
                    },
                ]

            }
        },
        watch: {
          css: {
            files: [
              'sass/**/*.sass',
              'scss/**/*.sass',
            ],
            tasks: ['compass']
          },
          js: {
              files: [
                 'src/mobile/mobile.js',
              ],
              tasks: ['concat']
          }
        },
        /*
        imagemin: {
            static: {
                options: {
                    optimizationLevel: 3,
                    svgoPlugins: [{ removeViewBox: false }],
                    use: [mozjpeg()]
                }
            }
        }
        */

    });

    grunt.registerTask('default', ['watch', 'compass', 'concat', 'uglify']);
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    //grunt.loadNpmTasks('grunt-contrib-imagemin');

};
