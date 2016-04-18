function TableOfContents(container, output) {
var toc = "";
var level = 0;
var container = document.querySelector(container) || document.querySelector('#contents');
var output = output || '#toc';

container.innerHTML =
    container.innerHTML.replace(
        /<h([\d])>([^<]+)<\/h([\d])>/gi,
        function (str, openLevel, titleText, closeLevel) {
            if (openLevel != closeLevel) {
                return str;
            }

            if (openLevel > level) {
                toc += (new Array(openLevel - level + 1)).join('<ul>');
            } else if (openLevel < level) {
                toc += (new Array(level - openLevel + 1)).join('</li></ul>');
            } else {
                toc += (new Array(level+ 1)).join('</li>');
            }

            level = parseInt(openLevel);

            var anchor = titleText.replace(/ /g, "_");
            toc += '<li><a href="#' + anchor + '">' + titleText
                + '</a>';

            //return '<h' + openLevel + '><a href="#' + anchor + '" id="' + anchor + '">'
            //    + titleText + '</a></h' + closeLevel + '>';
        }
    );

if (level) {
    toc += (new Array(level + 1)).join('</ul>');
}
document.querySelector(output).innerHTML += toc;
};


function create_toc_div () {
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

$(document).ready(function(){
    create_toc_div();
    TableOfContents('#notebook', '#toc')
});