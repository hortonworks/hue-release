# -*- encoding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1347633184.337
_enable_loop = True
_template_filename = 'C:/Users/Yuri/Desktop/python-project/sandbox_hue/auth/templates/base.html'
_template_uri = 'base.html'
_source_encoding = 'ascii'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'<div align="center">\r\n\t<h2>Sandbox</h2>\r\n\t<a href="/login/">Log In</a>\r\n\t<a href="/accounts/register/">Sign Up</a>\r\n</div>')
        return ''
    finally:
        context.caller_stack._pop_frame()


