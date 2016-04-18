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

var ol_depth = function (element) {
    // get depth of nested ol
    var d = 0;
    while (element.prop("tagName").toLowerCase() == 'ol') {
      d += 1;
      element = element.parent();
    }
    return d;
  };

function generate_toc(){
    var all_headers= $("#notebook").find(":header");
    var ul = $("<ul/>").addClass("toc-item");
    $("#toc").empty().append(ul);
    var depth = 1;
    var li= ul;//yes, initialize li with ul!
    var min_lvl=1, lbl_ary= [];
    for(; min_lvl <= 6; min_lvl++){ if(all_headers.is('h'+min_lvl)){break;} }
    for(var i= min_lvl; i <= 6; i++){ lbl_ary[i - min_lvl]= 0; }
    var newLine, el, title, link;

    all_headers.each(function (i, h) {
      var level = parseInt(h.tagName.slice(1), 10) - min_lvl + 1;
      // skip below threshold
      if (!h.id){ return; }

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

    return ul
}

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
          table_of_contents();
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
            id: "toc",
        })
    );

    $('<div/>', {
        class: 'col-md-2',
        id: 'toc-column',
    }).append(toc_wrapper).insertBefore('#notebook-container');



  };

$( document ).ready(function(){
    ToC = generate_toc();
    if (!$('#notebook').hasClass('row')) {
        create_toc_div();
        $('#notebook').addClass('row');
        $('#notebook-container').addClass('col-md-9').removeClass('container');
        $("#toc").empty().append(ToC);
    }
});


