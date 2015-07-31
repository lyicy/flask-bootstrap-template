# Template for a flask website

This repository contains everything to develop, test and deploy a flask
application on an Amazon EC2 instance.

It is pre-configured for efficient front-end development with [SASS][sass],
automated with [gulp][gulp].  The frontend template is based on
[zurb-foundation][zurb-foundation], and can be easily extended.

The template contains basic functionality for a blog with user management.
Blog entries are stored as YAML files, the user database is managed with either
a SQL database or a MongoDB NoSQL database.

## Why?

I started this project, because I want to streamline the deployment of
interactive websites.  This repository should include the greatest common
denominator of flask projects, that have a low user demand in the beginning of
their lifespan, but potential to grow quickly.  Starting a new project based on
this repository should minimize the configuration time and steps to get
something running.

Maybe it is useful for other people, too.  Feel free to add suggestions or to
send me a "Pull request".

## How to use it for your own website

In this section, we assume, that you want to 

1. 

## Questions

### When do you use gulp, when do you use fabric?

## TODO

- Figure out how to use Frozen-flask to create static webpages, because it
  really is very static right now.
- Add opengraph elements/twitter cards for blog entries
- Integrate the development process for javascript frontend application with
  react.js, including unit tests with jest
- Add integration testing with gulp-webdriver or python selenium?
- Add an admin page to actually make use of the login feature
- Add a 'comments' feature, maybe combined with logins?
- Maybe make this project a yeoman generator
- Figure out, how to use gulp-inline-css, to conform with Google Page style
  suggestions.
- Make an asynchronous installation with Tornado, because that is what I want
  to use in the future...


[sass]: http://www.sass-lang.com/
[gulp]: http://www.gulpjs.com/
[zurb-foundation]: http://foundation.zurb.com/
