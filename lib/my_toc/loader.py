from IPython.display import display, HTML, Javascript


def sidebar():
    from jsmin import jsmin
    with open('./lib/my_toc/2.0.js') as js_file:
        js = jsmin(js_file.read())
    js = "<script type='text/javascript'>" + js + '</script>'

    with open('./lib/my_toc/main.css', 'r') as myfile:
        css=myfile.read().replace('\n', '')
    css = "<style media='screen' type='text/css'>" + css + '</style>'
    return HTML(js+css)


def test_sidebar():
    lib_files = """ <script type='text/javascript' src='./lib/my_toc/2.0.js'></script>
        <link rel="stylesheet" type="text/css" href='./lib/my_toc/main.css' media="screen" />
        """
    return HTML(lib_files)