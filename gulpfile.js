/*
 * Copyright (c) 2013, Divio AG
 * Licensed under BSD
 * http://github.com/divio/djangocms-boilerplate-webpack
 */

// TODO:
// - The minimatch/graceful-fs warnings are from gulp, needs upgrade to 4.0 once released.

// #############################################################################
// IMPORTS
const argv = require('minimist')(process.argv.slice(2));
const gulp = require('gulp');

// #############################################################################
// SETTINGS
const DEBUG = argv.debug;
const PROJECT_ROOT = __dirname;
const PROJECT_PATH = {
    css: PROJECT_ROOT + '/static/css',
    // docs: PROJECT_ROOT + '/static/docs',
    // fonts: PROJECT_ROOT + '/static/fonts',
    // html: PROJECT_ROOT + '/templates',
    // images: PROJECT_ROOT + '/static/img',
    // icons: PROJECT_ROOT + '/private/icons',
    // js: PROJECT_ROOT + '/static/js',
    sass: PROJECT_ROOT + '/private/sass',
    // tests: PROJECT_ROOT + '/tests'
};
const PROJECT_PATTERNS = {
    // images: [
    //     PROJECT_PATH.images + '/**/*',
    //     // exclude from preprocessing
    //     '!' + PROJECT_PATH.images + '/dummy/*/**'
    // ],
    // js: [
    //     'gulpfile.js',
    //     './tools/tasks/**/*.js',
    //     PROJECT_PATH.js + '/**/*.js',
    //     PROJECT_PATH.tests + '/**/*.js',
    //     // exclude from linting
    //     '!' + PROJECT_PATH.js + '/*.min.js',
    //     '!' + PROJECT_PATH.js + '/**/*.min.js',
    //     '!' + PROJECT_PATH.js + '/dist/*.js',
    //     '!' + PROJECT_PATH.tests + '/coverage/**/*',
    //     '!' + PROJECT_PATH.tests + '/unit/helpers/**/*',
    //     '!' + PROJECT_PATH.tests + '/integration/*.bundle.js'
    // ],
    css: [
        PROJECT_PATH.css + '/*.css',
        '!' + PROJECT_PATH.css + '/*-critical.css'
    ],
    sass: [
        PROJECT_PATH.sass + '/**/*.{scss,sass}'
    ]
};
//
// var DEFAULT_PORT = 8000;
// var PORT = parseInt(process.env.PORT, 10) || DEFAULT_PORT;

// #############################################################################
// TASKS

/**
 * Checks project deployment
 * @param {String} id - task name
 * @returns {Object} - task which finished
 */
function task(id) {
    return require('./tools/tasks/' + id)(gulp, {
        PROJECT_ROOT: PROJECT_ROOT,
        PROJECT_PATH: PROJECT_PATH,
        PROJECT_PATTERNS: PROJECT_PATTERNS,
        DEBUG: DEBUG
        // PORT: PORT,
        // argv: argv
    });
}

/**
 * Usage:
 * - "gulp sass" (generates sass, splits the files, and injects the code)
 * - "gulp sass --debug" (to generate unminified css with sourcemaps)
 * - "gulp sass:compile" (just generates the base.css out of sass, handy to skip critical css)
 * - "gulp sass:critical" (splits the base.css with the critical css)
 * - "gulp sass:rest" (splits the base.css with the remaining "rest" css)
 * - "gulp sass:inline" (injects the base-critical.css as inline css into the template)
 */
gulp.task('sass', ['sass:critical', 'sass:rest', 'sass:inline']);
gulp.task('sass:compile', task('sass/compile'));
gulp.task('sass:critical', ['sass:compile'], task('sass/critical'));
gulp.task('sass:rest', ['sass:compile'], task('sass/rest'));
gulp.task('sass:inline', ['sass:critical'], task('sass/inline'));

// gulp.task('bower', task('bower'));
// gulp.task('lint:javascript', task('lint/javascript'));
// gulp.task('lint', ['lint:javascript']);
// gulp.task('sass', task('sass'));
// gulp.task('webpack:once', task('webpack/once'));
// gulp.task('webpack:watch', task('webpack/watch'));
// gulp.task('build', ['sass', 'webpack:once']);
//
// /**
//  * GULP_MODE === 'production' means we have a limited
//  * subset of tasks, namely sass, bower and lint to
//  * speed up the deployment / installation process.
//  */
// if (process.env.GULP_MODE !== 'production') {
//     gulp.task('images', task('images'));
//     gulp.task('docs', task('docs'));
//     gulp.task('preprocess', ['sass', 'images', 'docs']);
//     gulp.task('icons', task('icons'));
//
//     gulp.task('browser', task('browser'));
//
//     gulp.task('tests:lint', ['lint:javascript']);
//     gulp.task('tests:unit', task('tests/unit'));
//     gulp.task('tests:watch', ['tests:lint'], task('tests/watch'));
//     gulp.task('tests', ['tests:unit', 'tests:lint']);
//     gulp.task('tests:integration:webpack', task('tests/webpack'));
//
//     // Running integration tests on CI is usually problematic,
//     // since the environment to test against must be prepared.
//     // It is possible, but shouldn't be enforced by default.
//     gulp.task('tests:integration', ['tests:integration:webpack'], task('tests/integration'));
// }
//
gulp.task('default', ['sass']);
gulp.task('watch', function () {
    // gulp.start('webpack:watch');
    gulp.watch(PROJECT_PATTERNS.sass, ['sass']);
    // gulp.watch(PROJECT_PATTERNS.js, ['lint']);
});
//
// gulp.task('default', ['bower', 'sass', 'lint', 'watch']);
