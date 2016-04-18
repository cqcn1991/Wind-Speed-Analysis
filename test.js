var threshold = 6
var toc_cell=false;
var number_sections = true;
var rendering_toc_cell = false;
var config_loaded = false;
var extension_initialized=false;

//......... utilitary functions............

function incr_lbl(ary, h_idx){//increment heading label  w/ h_idx (zero based)
      ary[h_idx]++;
      for(var j= h_idx+1; j < ary.length; j++){ ary[j]= 0; }
      return ary.slice(0, h_idx+1);
  }

var make_link = function (h, num_lbl) {
    var a = $("<a/>");
    a.attr("href", '#' + h.attr('id'));
    // get the text *excluding* the link text, whatever it may be
    var hclone = h.clone();
    if( num_lbl ){ hclone.prepend(num_lbl); }
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
    $('#notebook').addClass('row');
    $('#notebook-container').addClass('col-md-9').removeClass('container');

  };

var table_of_contents = function () {
    if(rendering_toc_cell) { // if toc_cell is rendering, do not call  table_of_contents,                             
        rendering_toc_cell=false;  // otherwise it will loop
        return}

    var toc_wrapper = $("#toc-wrapper");
    var toc_index=0;
    if (toc_wrapper.length === 0) {
      create_toc_div();
    }
    var segments = [];
    var ul = $("<ul/>").addClass("toc-item");
    $("#toc").empty().append(ul);

    var cell_toc_text = "# Table of Contents\n <p>";
    var depth = 1;
    var li= ul;//yes, initialize li with ul! 
    var all_headers= $("#notebook").find(":header");
    var min_lvl=1, lbl_ary= [];
    for(; min_lvl <= 6; min_lvl++){ if(all_headers.is('h'+min_lvl)){break;} }
    for(var i= min_lvl; i <= 6; i++){ lbl_ary[i - min_lvl]= 0; }

    //loop over all headers
    all_headers.each(function (i, h) {
      var level = parseInt(h.tagName.slice(1), 10) - min_lvl + 1;
      // skip below threshold
      if (!h.id){ return; }
      var num_str= incr_lbl(lbl_ary,level-1).join('.');// numbered heading labels
      var num_lbl= $("<span/>").addClass("toc-item-num")
            .text(num_str).append('&nbsp;').append('&nbsp;');

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

        if (!$(h).attr("saveid")) {$(h).attr("saveid", h.id)} //save original id
        h.id=$(h).attr("saveid")+'-'+num_str;  // change the id to be "unique" and toc links to it

      // Create toc entry, append <li> tag to the current <ol>. Prepend numbered-labels to headings.
      li=$("<li/>").append( make_link( $(h), num_lbl));
      ul.append(li);
      if( number_sections ){ $(h).prepend(num_lbl); }

      //toc_cell:
      if(toc_cell) {
          var tabs = function(level) {
                var tabs = '';
                for (var j = 0; j < level -1; j++) { 
                  tabs += "\t";}
                  return tabs}

          var leves='<div class="lev'+level.toString()+'">'
          var lnk=make_link($(h))
          cell_toc_text += leves + $('<p>').append(lnk).html()+'</div>';
      }
    });

};
    
var toggle_toc = function () {
    // toggle draw (first because of first-click behavior)
    $("#toc-column").toggle({duration:0, complete:function(){
        $('#notebook-container').toggleClass("col-md-9").toggleClass("col-md-10 col-md-offset-1");
      }
    });

    IPython.notebook.set_dirty();
    // recompute:
    rendering_toc_cell = false;
    table_of_contents();
  };
  

var load_ipython_extension = function () {
    // render toc on load
    $([IPython.events]).on("notebook_loaded.Notebook", function(){ // curiously, the event is not always fired or detected
                                                       // thus I rely on kernel_ready.Kernel to read the initial config 
                                                       // and render the first  table of contents
        table_of_contents();
        // render toc for each markdown cell modification
        //$([IPython.events]).on("rendered.MarkdownCell", table_of_contents);
        $([IPython.events]).on("rendered.MarkdownCell", function(){table_of_contents();});
            console.log("toc2 initialized (via notebook_loaded)")
        extension_initialized=true  ; // flag to indicate that initialization was done
})

    $([IPython.events]).on("kernel_ready.Kernel", function(){
        if (!extension_initialized){
            table_of_contents();
            // render toc for each markdown cell modification
            $([IPython.events]).on("rendered.MarkdownCell", function(){table_of_contents();});
            console.log("toc2 initialized (via kernel_ready)")
        }
    });

  };
$( document ).ready(load_ipython_extension);