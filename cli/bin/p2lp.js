#!/usr/bin/env node
// bin/p2lp.js — paper-to-learning-path CLI entry point

'use strict';

const path = require('path');
const { run } = require('../src/cli');

run(process.argv.slice(2));
