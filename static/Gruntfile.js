module.exports = function( grunt ) {
    "use strict";

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
            weixin: {
                src: ['src/mobile/lib/zepto/zepto.js', 'src/mobile/mobile.js'],
                dest: 'scripts/mobile/mobile.js',
            },
            acOne: {
                src: ['src/mobile_activity/lib/zepto.min.js', 'src/mobile_activity/lib/ac_mod.js', 'src/mobile_activity/activityName.js'],
                dest: 'scripts/mobile_activity/activityName.js',
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
                  'src/mobile_activity/*.js',
              ],
              tasks: ['concat']
          }
        }

    });

    grunt.registerTask('default', ['watch', 'compass', 'concat', 'uglify']);
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
};
