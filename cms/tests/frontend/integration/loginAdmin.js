'use strict';

// #############################################################################
// Init all settings and event handlers on suite start

require('./../casperjs.conf').init();

require('./handlers/pageErrors').bind();
require('./handlers/loadFailures').bind();
require('./handlers/missingPages').bind();
require('./handlers/externalMissing').bind();
require('./handlers/suiteFailures').bind();


// #############################################################################
// User login via the admin panel

var globals = require('./settings/globals');
var messages = require('./settings/messages').login.admin;

casper.test.begin('User Login (via Admin Panel)', function (test) {
    casper
        .start(globals.adminUrl, function () {
            var titleRegExp = new RegExp(globals.adminTitle, 'g');

            test.assertTitleMatch(titleRegExp, messages.cmsTitleOk);
            test.assertExists('#login-form', messages.adminAvailable);

            this.fill('#login-form', {
                username: 'fake',
                password: 'credentials'
            }, true);
        })
        .waitForSelector('.errornote', function () {
            test.assertExists('.errornote', messages.loginFail);

            this.fill('#login-form', globals.credentials, true);
        })
        .thenOpen(globals.baseUrl, function () {
            test.assertExists('.cms-toolbar', messages.loginOk);
        })
        .run(function () {
            test.done();
        });
});
