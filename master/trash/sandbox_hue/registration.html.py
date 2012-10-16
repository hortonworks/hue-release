# -*- encoding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1347631582.2
_enable_loop = True
_template_filename = 'C:/Users/Yuri/Desktop/python-project/sandbox_hue/auth/templates/registration.html'
_template_uri = 'registration.html'
_source_encoding = 'ascii'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        users = context.get('users', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        for u in users:
            # SOURCE LINE 2
            __M_writer(u'\t')
            __M_writer(unicode(u.password))
            __M_writer(u'<br/>\r\n\t')
            # SOURCE LINE 3
            __M_writer(unicode(u.phone))
            __M_writer(u'<br/>\r\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


