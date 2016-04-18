from IPython.display import display, HTML


def output_HTML(read_file, output_file):
    from nbconvert import HTMLExporter
    import codecs
    import nbformat
    exporter = HTMLExporter()
    # read_file is '.ipynb', output_file is '.html'
    output_notebook = nbformat.read(read_file, as_version=4)
    output, resources = exporter.from_notebook_node(output_notebook)
    codecs.open(output_file, 'w', encoding='utf-8').write(output)


def toggle_cell():
    toggle = '''<script>
    code_show=false;
    function code_toggle() {
     if (code_show){
     $('div.input').hide();
     } else {
     $('div.input').show();
     }
     code_show = !code_show
    }
    $( document ).ready(code_toggle);
    </script>
    <form action="javascript:code_toggle()"><input type="submit" value="Click here to toggle on/off the raw code."></form>'''
    return HTML(toggle)


def sidebar():
    from jsmin import jsmin
    with open('./lib/my_toc/1.0.js') as js_file:
        js = jsmin(js_file.read())
    js = "<script type='text/javascript'>"+js +'</script>'

    with open('./lib/my_toc/main.css', 'r') as myfile:
        css=myfile.read().replace('\n', '')
    css = "<style media='screen' type='text/css'>"+css +'</style>'
    # """ <script type='text/javascript' src='./lib/my_toc/1.0.js'></script>
    #     <link rel="stylesheet" type="text/css" href='./lib/my_toc/main.css' media="screen" />
    #     """
    return HTML(js+css)


def load_libs():
    display(toggle_cell())
    display(sidebar())