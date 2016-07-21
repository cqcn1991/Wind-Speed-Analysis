function hide_previous_output(){
    console.log('Hello World, this is output_and_hide');
    $('.hide-prompt').closest('.output_area').siblings().addClass( "hide");
}

function sleep (time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}

function bind_hide_as_buttons() {
    console.log('This is button');
    $('.hide-prompt').click(function() {
        console.log('button clicked');
        $(this).closest('.output_area').siblings().toggleClass("hide");
});
}


$( document ).ready(function(){
    if (typeof IPython != "undefined") {
      $([IPython.events]).on("output_appended.OutputArea", function(){
        sleep(1000).then(() => {
            hide_previous_output();
            console.log('code executed');
        });
    });}
});
