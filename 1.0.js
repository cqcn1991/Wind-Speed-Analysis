var make_link = function (h) {
    var a = $("<a/>");
    a.attr("href", '#' + h.attr('id'));
    // get the text *excluding* the link text, whatever it may be
    var hclone = h.clone();
    hclone.children().last().remove(); // remove the last child (that is the automatic anchor)
    hclone.find("a[name]").remove();   //remove all named anchors
    a.html(hclone.html());
    //console.log("h",h.children)
    return a;
  };


var generate_toc = function (){
    var all_headers= $("#notebook").find(":header");
    var ul = $("<ul/>").addClass("toc-item");
    $("#toc").empty().append(ul);
    var depth = 1;
    var li= ul;//yes, initialize li with ul!
    var min_level = 3;

    all_headers.each(function (i, h) {
      var level = parseInt(h.tagName.slice(1), 10);
      // skip below threshold
      if (level> min_level){ return; }

      // walk down levels
      for(var elm=li; depth < level; depth++) {
          var new_ul = $("<ul/>").addClass("toc-item");
          elm.append(new_ul);
          elm= ul= new_ul;
      }
      // walk up levels
      for(; depth > level; depth--) {
          // up twice: the enclosing <ol> and <li> it was inserted in
          ul= ul.parent();
          while(!ul.is('ul')){ ul= ul.parent(); }
      }

      // Create toc entry, append <li> tag to the current <ol>. Prepend numbered-labels to headings.
      li=$("<li/>").append(make_link($(h)));
      ul.append(li);
        });

   //
   //  return ul
};

var generate_toc_all = function(){
    generate_toc();
    // var ToC = generate_toc();
    // $("#toc").empty().append(ToC);
};

var create_toc_div = function () {
    var toc_wrapper = $('<div id="toc-wrapper"/>')
    .append(
      $("<div/>")
      .addClass("header")
      .text("Contents ")
      .append(
        $("<a/>", {
            id: 'toc-reload-btn',
            href:'#',
            title:  'Reload ToC',
            text: "  \u21BB"
        }).click( function(){
          generate_toc_all();
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
            $('.toc-item-num').toggle();
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

var init_toc = function (){
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

$(document).ready(function(){
    if (!$('#notebook').hasClass('row')) {
        init_toc()
    }

    if (typeof IPython != "undefined") {
      $([IPython.events]).on("rendered.MarkdownCell", function(){
        generate_toc_all();
    });
    }

    generate_toc_all();
});


