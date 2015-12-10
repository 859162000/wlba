
module.exports = function (grunt) {
    "use strict";
    var config = {
        compass: {
            dist: {
                options: {
                    config: 'config_fuel.rb'
                }
            }
        },

        activityMod: ['src/mobile_activity/lib/zepto.util.js', 'src/mobile_activity/lib/activity.util.js'],

        concat: {
            options: {
                separator: ';'
            },
            basic: {
                files: {
                    'scripts/mobile/mobile.js': ['src/mobile/lib/zepto/zepto.js', 'src/mobile/mobile.js'],
                    'scripts/subMobile/mobile.js': ['src/subMobile/lib/zepto/zepto.js', 'src/subMobile/mobile.js'],
                }
            }
        },

        uglify: {
            build: {
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
                    {
                        expand: true,
                        cwd: 'scripts/app/',
                        src: '*.js',
                        dest: 'scripts/app/dist/'
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
                    'src/subMobile/*.js',
                    'src/app/*.js',
                ],
                tasks: ['concat']
            },
            grunt: {
                files: ['Gruntfile.js', 'webpack.dev.config.js'],
                options: {
                    livereload: true
                }
            }
        }
    };


    grunt.file.recurse('src/mobile_activity/', function (abspath, rootdir, subdir, filename) {
        if (abspath.indexOf(subdir) < 0) {
            var key = 'scripts/mobile_activity/' + filename;
            config.concat.basic.files[key] = ['<%= activityMod %>', abspath]
        }
        return
    });

    grunt.file.recurse('src/app/', function (abspath, rootdir, subdir, filename) {
        if (abspath.indexOf(subdir) < 0) {
            var key = 'scripts/app/' + filename;
            config.concat.basic.files[key] = ['<%= activityMod %>', abspath]
        }
        return
    });

    grunt.initConfig(config);
    require('load-grunt-tasks')(grunt);

    grunt.registerTask('default', ['watch', 'compass', 'concat', 'uglify']);

    grunt.registerTask( 'build', ['uglify:build'] );

    //加油卡sass
    grunt.registerTask("fuel-dev", function(){
        grunt.task.run(['compass', 'watch']);
        grunt.log.writeln('--------加油卡--------')

    });


};
