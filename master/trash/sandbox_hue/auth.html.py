# -*- encoding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1347633337.222
_enable_loop = True
_template_filename = 'C:/Users/Yuri/Desktop/python-project/sandbox_hue/auth/templates/auth.html'
_template_uri = 'auth.html'
_source_encoding = 'ascii'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        auth = context.get('auth', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'<!DOCTYPE>\r\n<html>\r\n\t<head>\r\n\t\t<title></title>\r\n\t</head>\r\n\t<body>\r\n')
        # SOURCE LINE 7
        if auth:
            # SOURCE LINE 8
            __M_writer(u'\t\t\t<form action="" method="post">\r\n\t\t\t\t<input type="submit" name="logout" value="logout"/>\r\n\t\t\t</form>\r\n')
            # SOURCE LINE 11
        else:
            # SOURCE LINE 12
            __M_writer(u'\t\t\t<form action="" method="post">\r\n\t\t\t\t<div>Login</div>\r\n\t\t\t\t<input type="text" name="username"/><br/>\r\n\t\t\t\t<div>Password</div>\r\n\t\t\t\t<input type="password" name="password"/><br/>\r\n\t\t\t\t<input type="submit" name="login" value="login"/>\r\n\t\t\t</form>\r\n')
        # SOURCE LINE 20
        __M_writer(u'\t\t<a href="/"><- Back</a>\r\n\t</body>\r\n</html>')
        return ''
    finally:
        context.caller_stack._pop_frame()


