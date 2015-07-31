# -*- coding: utf-8 -*-
import markdown
from dateutil.parser import parse as dateparse
from os import listdir
from os.path import splitext, abspath, join as pjoin
from datetime import datetime

from ..utils import slugify


class Cache(object):

    def __init__(self, blog):
        self.filled = False
        self.blog = blog
        self.documents = []
        self.category_index = {}
        self.category_names = {}
        self.slug_index = {}

    def parse_meta(self, meta):
        res = {
            'title': '',
            'authors': [''],
            'date': datetime.now(),
            'summary': '',
            'categories': ['Default'],
            }
        for key, value in meta.iteritems():
            if key in ['date', 'updated']:
                res[key] = dateparse(' '.join(value))
            elif key in ['summary', 'title', 'slug']:
                res[key] = '\n'.join(value).strip()
            elif key in ['categories']:
                res['category_slugs'] = [slugify(c) for c in value]
                res[key] = value
            else:
                res[key] = value

        if 'slug' not in res:
            if 'title' in res:
                res['slug'] = slugify(res['title'])
            else:
                raise ValueError('No slug definition for blog entry found')
        if 'updated' not in res:
            res['updated'] = res['date']

        res['slug'] = res['slug'].lower()
        return res

    def _read(self, mdfile):
        md = markdown.Markdown(
            # 'markdown.extensions.extra',
            # 'markdown.extensions.admonition',
            extensions=[
                'markdown.extensions.meta'],
            output_format='html5')
        with open(mdfile, 'r') as fh:
            text = fh.read()
            html = md.convert(text)
            document = {
                'html': html}
            document.update(self.parse_meta(md.Meta))

        return document

    def cache_all_blogs(self):
        candidates = sorted(listdir(self.blog.blog_dir))
        mdfiles = [
            abspath(pjoin(self.blog.blog_dir, c)) for c in candidates if (
                splitext(c)[1] in ['.md', '.markdown', '.mdown'])]

        for i, mdfile in enumerate(mdfiles):
            document = self._read(mdfile)
            for cat in document['categories']:
                scat = slugify(cat)
                self.category_names[scat] = cat
                if scat in self.category_index:
                    cindex = self.category_index[scat]
                else:
                    cindex = self.category_index[scat] = []
                cindex.append(i)

            self.slug_index[document['slug']] = i

            self.documents.append(document)
        self.filled = True

    def get_blog(self, slug):
        if not self.filled:
            self.cache_all_blogs()

        slug_index = self.slug_index[slug]
        return self.documents[slug_index]

    def list_blogs(self, category=None):
        if not self.filled:
            self._cache_all_blogs()

        if category:
            return [self.documents[i] for i in self.category_index[category]]
        else:
            return self.documents


class Blog(object):

    def init_app(self, app, fill_cache=True):
        self.app = app
        # I really do not know, if we need to make this a local proxy or
        # something like that...
        self.cache = Cache(self)
        self.cache.cache_all_blogs()
        app.jinja_env.globals['blogs'] = self

    @property
    def blog_dir(self):
        return self.app.config.get('FLASK_BLOG_DIR', None)

    def get_blog(self, slug):
        """
        partial information about a blog entry
        """
        return self.cache.get_blog(slug)

    def list_blogs(self, category=None):
        """
        list all blog entries in a category, or in all categories
        """
        return self.cache.list_blogs(category)

    def get_category_name(self, category_slug):
        return self.cache.category_names[category_slug]

    def get_categories(self):
        return self.cache.category_names

# vim:set ft=python sw=4 et spell spelllang=en:
