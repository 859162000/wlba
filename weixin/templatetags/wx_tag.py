# encoding:utf-8
from __future__ import unicode_literals
from django import template
from django.core.urlresolvers import reverse

register = template.Library()


class NavTagItem(template.Node):
    def __init__(self, view_name, nav_displaytext):
        self.path = reverse(view_name) if view_name != '#' else view_name
        self.text = nav_displaytext.strip('"')

    def render(self, context):
        cur_path = context['request'].path
        current = cur_path == self.path
        cur_class = ['', ' active'][current]
        return '<a class="item{}" href="{}">{}</a>'.format(cur_class, self.path, self.text)


@register.tag
def nav_tag_item(parser, token):
    try:
        tag_name, nav_path, nav_text = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, \
            "%r tag requires exactly two arguments: path and text" % \
            token.split_contents[0]

    return NavTagItem(nav_path, nav_text)
