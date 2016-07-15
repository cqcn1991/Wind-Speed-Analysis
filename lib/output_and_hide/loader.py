from IPython.display import display, HTML, Javascript


def output_and_hide_button():
    from jsmin import jsmin
    with open('./lib/my_toc/1.0.js') as js_file:
        js = jsmin(js_file.read())
    js = "<script type='text/javascript'>" + js + '</script>'
    return HTML(js)


def test_output_and_hide():
    lib_files = """ <script type='text/javascript' src='./lib/output_and_hide/1.0.js'></script>
        """
    return HTML(lib_files)


