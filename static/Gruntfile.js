module.exports = function (grunt) {
    "use strict";
    var webpack = require('webpack'),
        webpackConfig = require('./webpack.dev.config.js');
    var config = {
        compass: {
            dist: {
                options: {
                    config: 'config_weixin.rb'
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
                    'scripts/mobile/mobile.js': ['src/mobile/lib/zepto/zepto.js', 'src/mobile/mobile.js']
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
        webpack: {
            options: webpackConfig,
            build: {
				plugins: webpackConfig.plugins.concat(
					new webpack.DefinePlugin({
						"process.env": {
							"NODE_ENV": JSON.stringify("production")
						}
					}),
					new webpack.optimize.DedupePlugin(),
					new webpack.optimize.UglifyJsPlugin()
				)
			},
            "build-dev": {
				debug: false
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
                    'src/app/*.js',
                ],
                tasks: ['concat']
            },
            webpack: {
                files: ['test/**/*', 'webpack.config.js', 'Gruntfile.js'],
                tasks: ['webpack:build-dev'],
                options: {
                    livereload: true,
                    spawn: false
                }
            }
        }

    };


    grunt.file.recurse('src/mobile_activity/', function (abspath, rootdir, subdir, filename) {
        if (abspath.indexOf(subdir) < 0) {
            var key = 'scripts/mobile_activity/' + filename
            config.concat.basic.files[key] = ['<%= activityMod %>', abspath]
        }
        return
    })

    grunt.file.recurse('src/app/', function (abspath, rootdir, subdir, filename) {
        if (abspath.indexOf(subdir) < 0) {
            var key = 'scripts/app/' + filename
            config.concat.basic.files[key] = ['<%= activityMod %>', abspath]
        }
        return
    })

    grunt.initConfig(config);
    require('load-grunt-tasks')(grunt);
    grunt.registerTask('default', ['watch', 'compass', 'concat', 'uglify']);

    grunt.registerTask('build', ['uglify:build']);

    // Webpack tasks
    grunt.registerTask("dev", ['webpack:build-dev', 'watch:app']);   // Development build
    grunt.registerTask("build", ["webpack:build"]);
};
