zombie-radar
============

A set of modules for watching the zombie levels across a region in near-real time.

Do not use in a way that does not comply with the API Rate limits, please.

## Dependencies

1. python 2.7
2. [trawler daemon](https://github.com/Eluvatar/trawler-daemon-c)
3. python zmq
4. (optional) python progressbar

## Execution

First, you must have transmission running in the background, e.g.:

```bash
$ ./transmission_runner.py -u 'Your Nation Name' (Replace with something appropriate)
```

Secondly, you need to start the actual zombie radar driver:

```bash
$ ./runner -u 'Your Nation Name' 'Your Region' (Replace)
```

I would recommend running both of these in a terminal multiplexer such as [screen](https://en.wikipedia.org/wiki/GNU_Screen) or [tmux](https://en.wikipedia.org/wiki/Tmux).

Finally, to actually show the collected and updated data to your region-mates, you need to publish a web page, like this:

```html
<html>
<head>
<title>Zombie Observation Post</title>
<script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
<script type="text/javascript" src="http://z5.ifrm.com/9057/121/0/f5151052/jquerytablesortermin.js"></script>
<script type="text/javascript">
var region_name = 'Your Region';
var server = 'your.server.address';

var region = region_name.toLowerCase().replace(/ /g,'_')


function action_filter(action) {
  $('#top_nations tbody tr').hide();
  $('.'+action).show();   
}

function show_ratios() {
  $("#top_nations .ratio").show();
}

function action_filter(action) {
  $('#top_nations tbody tr').hide();
  $('.'+action).show();
}

$(document).ready(function(){
  $.getJSON("http://"+server+":6264/"+region, function(data) {
    $("noscript").after('<p style="font-style:italic; font-weight:bold; font-size:12pt;">'+region_name+' Nations</p><p>by survivors, zombies, or dead</p><p>Filter by <a href="#research" onclick="action_filter('+"'research'"+');" name="show_all">research</a>, <a href="#exterminate" onclick="action_filter('+"'exterminate'"+');" name="show_all">exterminate</a>, <a href="#export" onclick="action_filter('+"'export'"+');" name="show_all">export</a>, or <a href="#null" onclick="action_filter('+"'null'"+');" name="show_all">considering options</a>.</p>',$("<table>",{
      id:'top_nations',
      class:'tablesorter',
      width:'300'
    }).append('<thead><tr><th>#</th><th>Nation</th><th>Survivors</th><th>Zombies</th><th>Dead</th></tr></thead>',$('<tbody>').append($.map( data, function(nation,idx){
      return '<tr class="'+(nation.action ? nation.action : 'null' )+'"><th>'+(idx+1)+'</th><th><a href="https://www.nationstates.net/nation='+nation.name+'">'+nation.name+'</a></th><td>'+nation.survivors+'<td>'+nation.zombies+'</td><td>'+nation.dead+'</td></tr>' ;
    }).join())));
    $("#top_nations").tablesorter({sortList:[[3,1]],headers:{0:{sorter:false},1:{sorter:false}}});
    $("#top_nations").bind('sortStart',function(){
      $("#top_nations tbody th:first-child").text(function(idx,o){return '';});
    }).bind('sortEnd',function(){
      $("#top_nations tbody th:first-child").text(function(idx,o){return idx+1;});
    });
    if( window.location.hash ) {
      document.getElementById('top_nations').scrollIntoView(true);
      var action = {'#null':'null','#research':'research','#exterminate':'exterminate','#export':'export'}[window.location.hash];
      if( action ){
        action_filter(action);
      }
    }
  });
});
</script>
<center><h1>Zombie Observation Post</h1>
<img src="http://some.site.com/your_regional_image.jpg" alt="">
<br><noscript><p style="font-style:italic; font-weight:bold; font-size:12pt; color:red;">Because you have javascript disabled, this page will not work.</p></noscript>
</center>
</body>
</html>
```

I would of course recommend adjusting the page to fit with your regional aesthetics.
