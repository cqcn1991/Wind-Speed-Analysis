function generate_toc_content(){
    var all_headers= $("#notebook").find(":header");
    var toc = "";
    var level = 0;
    var min_level = 3;

    all_headers.each(function (i, h) {
        var openLevel = parseInt(h.tagName.slice(1), 10);
        if (openLevel>min_level) {return;}
        var titleText = $(h).clone()    //clone the element
                            .children() //select all the children
                            .remove()   //remove all the children
                            .end()  //again go back to selected element
                            .text();
        if (openLevel > level) {
            toc += (new Array(openLevel - level + 1)).join("<ol class='toc-item unstyle'>");
        } else if (openLevel < level) {
            toc += (new Array(level - openLevel + 1)).join('</li></ol>');
        } else {
            toc += (new Array(level+ 1)).join('</li>');
        }
        level = parseInt(openLevel);
        var anchor = $(h).attr('id');
        toc += '<li><a href="#' + anchor + '">' + titleText
            + '</a>';
        }
    );

if (level) {
    toc += (new Array(level + 1)).join('</ol>');
}
    return toc
}

function show_list_number () {
    $("#toc ol").toggleClass('unstyle');
    $("#toc ol").toggleClass('nested');
    $("#toc li").toggleClass('nested');
};

var create_toc_div = function () {
    var toc_wrapper = $('<div id="toc-wrapper"/>')
    .append(
      $("<div/>",{
          class: 'header',
          text: 'Contents '
      }).append(
        $("<a/>", {
            id: 'toc-reload-btn',
            href:'#',
            title:  'Reload ToC',
            text: "  \u21BB"
        }).click( function(){
          create_toc();
          return false;
        })
      ).
      append(
        $("<a/>", {
            id: 'display-heading-number-btn',
            href:'#',
            title:  'Number text sections',
            text: '#'
        }).click( function(){
            show_list_number();
        })
      )
    ).append(
        $("<div/>", {
            id: "toc"
        })
    );

    $('<div/>', {
        class: 'col-md-2',
        id: 'toc-column'
    }).append(toc_wrapper).insertBefore('#notebook-container');
    
  };

var toggle_toc = function () {
    $("#toc-column").toggle({duration:0, complete:function(){
        $('#notebook-container').toggleClass("col-md-9").toggleClass("col-md-10 col-md-offset-1");
      }
    });
  };


var init_toc_container = function (){
    if ($("#toc_button").length === 0) {
        if (typeof IPython != "undefined") {
        IPython.toolbar.add_buttons_group([
        {'label'   : 'Table of Contents',
          'icon'    : 'fa-list',
          'callback': toggle_toc,
          'id'      : 'toc_button'
        }
        ]);}}
    create_toc_div();
    $('#notebook').addClass('row');
    $('#notebook-container').addClass('col-md-9').removeClass('container');
};

var create_toc = function () {
    var ToC = generate_toc_content();
    $("#toc").empty().append(ToC);
};

$( document ).ready(function(){
    if (!$('#notebook').hasClass('row')) {
        init_toc_container()
    }

    if (typeof IPython != "undefined") {
      $([IPython.events]).on("rendered.MarkdownCell", function(){
        create_toc();
    });
    }
    create_toc();

});


