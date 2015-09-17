module.exports = function( grunt ) {
    "use strict";

    var config =  {
        compass: {
            dist: {
                options: {
                    config: 'config.rb'
                }
            }
        },
        activityMod: ['src/mobile_activity/lib/zepto.util.js', 'src/mobile_activity/lib/activity.util.js'],

        concat: {
            options: {
                separator: ';'
            },
            basic:{
                files: {
                    'scripts/mobile/mobile.js': ['src/mobile/lib/zepto/zepto.js', 'src/mobile/mobile.js'],
                }
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

    };


    grunt.file.recurse('src/mobile_activity/', function(abspath, rootdir, subdir, filename){
        if(abspath.indexOf(subdir) < 0){
            var key  = 'scripts/mobile_activity/'+filename
            config.concat.basic.files[key] = ['<%= activityMod %>', abspath]
        }
        return
    })

    grunt.initConfig(config);

    grunt.registerTask('default', ['watch', 'compass', 'concat', 'uglify']);

    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
};
