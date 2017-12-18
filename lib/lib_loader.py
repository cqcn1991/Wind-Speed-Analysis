from IPython.display import display, HTML, Javascript
from .my_toc.loader import *


def align_figures():
    import matplotlib
    from matplotlib._pylab_helpers import Gcf
    from IPython.display import display_html
    import base64
    from ipykernel.pylab.backend_inline import show

    images = []
    for figure_manager in Gcf.get_all_fig_managers():
        fig = figure_manager.canvas.figure
        png = get_ipython().display_formatter.format(fig)[0]['image/png']
        src = base64.encodestring(png).decode()
        images.append('<img style="margin:0" align="left" src="data:image/png;base64,{}"/>'.format(src))

    html = "{}".format("".join(images))
    show._draw_called = False
    matplotlib.pyplot.close('all')
    display_html(html, raw=True)


def hide_as(button_text='+/-'):
    button = "<button class='hide-prompt'>" + button_text + "</button>"
    return HTML(button)


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


def save_notebook():
    return display(Javascript("IPython.notebook.save_notebook()"),
                   include=['application/javascript'])



def load_libs():
    display(toggle_cell())
    # display(sidebar())


def test_libs():
    display(test_output_and_hide())