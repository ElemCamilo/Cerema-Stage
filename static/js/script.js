

//Ici les fonctions pour faire AJAX avec Javascript
function loadDoc(url) {
  //la variable ur contient l'id qui est une variable obtenue depuis la BD par Python
  var xhttp;
  xhttp=new XMLHttpRequest();
  xhttp.open("GET", url, true);
  xhttp.send();
}


function data() 
{
    document.getElementById('hello').style.color = 'blue';
    var tuple_1 = "("+document.getElementById('Tripnumber').value+",Tripnumber)";
    var tuple_2 = "("+document.getElementById('DriverID').value+",DriverID)";
    var tuple_3 = "("+document.getElementById('SystemType').value+",SystemType)";
    var to_send = "/first_map?Tripnumber="+tuple_1+"&DriverID="+tuple_2+"&SystemType="+tuple_3; 
    loadDoc(to_send);
}



