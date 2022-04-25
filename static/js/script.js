
function data() 
{
    var tuple_1 = document.getElementById('Tripnumber').value+",Tripnumber";
    var tuple_2 = document.getElementById('DriverID').value+",DriverID";
    var tuple_3 = document.getElementById('SystemType').value+",SystemType";
    var liste = [[tuple_1],[tuple_2],[tuple_3]];
    var liste_str = liste.toString();
    document.getElementById('liste_data').value = liste_str;
	document.getElementById('liste_data_f').submit();
}



