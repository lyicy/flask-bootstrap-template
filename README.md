# Template for a flask website

This repository contains everything to develop, test and deploy a flask
application on an Amazon EC2 instance.

It is pre-configured for efficient front-end development with [SASS][sass],
automated with [gulp][gulp].  The frontend template is based on
[bootstrap][bootstrap].  I try to keep it [as semantic and small as
possible](http://www.tallygist/blog/web-development/semantic-bootstrap).

The template contains basic functionality for a blog with user management.
Blog entries are stored as YAML files, the user database is managed with a
MongoDB NoSQL database.  The repository history contains a version with an
SQLAlchemy back-end as well.

## Why?

I learned web development by doing -- probably like most people.  This
project serves several purposes:

1. It is a documentation of the best practices that I found for myself.  These
   practices are explained in my [blog](http://www.tallygist.com/).  They will
   change over time, of course.
2. It is a documentation of the most common problems, that I am encountering
   while developing and launching web sites.
3. It is a template for bootstrapping new projects.  This file should include
   all the steps, that are necessary to deploy the website on an Amazon EC2
   instance and configure it.

While it is a very personal project, based on my personal ideas on how to
streamline the process of web development, I hope that it can be of value for
other people, too:

- If you are just starting to explore the web-development world, this project
  might be a good demo/tutorial to find out about many of the steps that are
  involved.
- If have already established your own opinions about how to develop and deploy
  a website, I am excited to hear about them, and discuss them with you.  One
  of the great things about web-development is, that you work with the entire
  world.

## Installation

After checking out your working copy of `flask-blog-bootstrap` project, you
have to install several dependencies:

Node packages can be installed with:

    npm install

The JavaScript dependencies for the website are managed by [bower][bower]:

    bower install

For the back-end, you might need to install some python dependencies:

    cd app
    pip install -r requirements.txt -r requirements_dev.txt


## Configuration

The project comes with dummy configuration files, however, you probably want to
customize them.

1. Create a configuration directory somewhere on your computer, preferably with
   version control.
2. Create a directory where you want to store your own blog posts, preferably
   with version control.
3. Copy the files `app/configurations/empty.py` and `app/fabfile_sample.yaml`
   into the configuration directory, and rename them to something more
   meaningful.
4. Change the configuration variables in these two files.
5. Set two environment variables:

    export FLASK_BLOG_SETTINGS=/path/to/your/configuration.py
    export FABFILE_CONFIGURATION=/path/to/your/deployment/configuration.yaml

Now, the project should be customized to your own needs.

If you just want to add your own blog, you can start creating your own posts in
the blog post directory.  They need to be formatted like the example files in
the directory `app/test_blogs/`.

Run the local development server

    gulp serve:dist

in order to check that the result looks as you expect it.  If you add blog
posts to your directory, or change existing ones, right now you have to restart
the back-end server manually:

    gulp flask-restart:dist

!!! Note:

  The `flask-blog-bootstrap` code includes a user database, allowing users to
  register and login to your website.  Currently, this feature is not utilized,
  but in order to store the user data, a Mongo database connection is
  necessary.  Managed databases are awesome, and for such a small project, you
  can get it for free, for example from [mongolab][mongolab].

## Development process

If you want to change the front-end template files, or add back-end
functionality, start the development server first:

    gulp serve

Every change in yonder the `app/flask_blog` directory, should reload the server
automatically.

### How do I add a new website?

1. Create a new website in `app/flask_blog/templates`, that probably extends
   the `_bases/_headfoot_js.html` template.
2. Add a new view to the app eg., in `app/flask_blog/index/views.py`, that
   renders your template.

### How do I adapt the style sheets?

The main stylesheet is called created from an SCSS configuration at
`app/flask_blog/static/styles/main.css`, and is included in every website
template, that extends the `_bases/_headfoot_js.html` template. Every change to
this file is immediately reflected in your website.

## Deployment on an Amazon EC2 server

If you want to deploy the 
You only need


## Questions

### When do you use gulp, when do you use fabric?

## Links to my blog posts

- How to choose your web tools?
- Deployment with Amazon EC2...
- An odyssey with docker

## TODO

- Figure out how to use Frozen-flask to create static webpages, because it
  really is very static right now.
- Alternatively, integrate at least Flask-Cache and research if you have to do
  anything, such that jinja2 uses the BytecodeCaching loaders.
- Check if you can optimize the ETag meta information in requests, to optimize
  the browser caching.
- Add opengraph elements/twitter cards for blog entries
- Integrate the development process for javascript frontend application with
  react.js, including unit tests with jest
- Add integration testing with gulp-webdriver or python selenium?
- Add an admin page to actually make use of the login feature
- Add a 'comments' feature, maybe combined with logins?
- Make the blog cache a memcached/redis thing...
- Maybe make this project a yeoman generator
- Figure out, how to use gulp-inline-css and penthouse, to conform with page
  style suggestions and inline the "above-the-fold" styles.
- Experiments with uncss() could also be nice...
- Make an asynchronous installation with Tornado, because that is what I want
  to use in the future...
- add robots.txt


[sass]: http://www.sass-lang.com/
[gulp]: http://www.gulpjs.com/
[bootstrap]: http://getbootstrap.com/
[bower]: http://bowerjs.com/
[mongolab]: http://mongolab.com/

<!-- vim: set ft=markdown et spell spelllang=en: -->
