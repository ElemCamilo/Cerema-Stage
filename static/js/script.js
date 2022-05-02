
function data() 
{
    var tuple_1 = document.getElementById('Tripnumber').value+",Tripnumber";
    var tuple_2 = document.getElementById('DriverID').value+",DriverID";
    var tuple_4 = document.getElementById('SpeedLimit').value+",SpeedLimit";
    var tuple_5 = document.getElementById('InstantSpeed_CAN').value+",InstantSpeed_CAN";
    var tuple_6 = document.getElementById('CumFuel').value+",CumFuel";
    var tuple_7 = document.getElementById('Accel_Position').value+",Accel_Position";
    var tuple_8 = document.getElementById('Distance_cum').value+",Distance_cum";
    var tuple_9 = document.getElementById('OverSpeed').value+",OverSpeed";
    var tuple_10 = document.getElementById('smoothed_Acceleration_MM').value+",smoothed_Acceleration_MM";
    var tuple_11 = document.getElementById('smoothed_Jerk_MM').value+",smoothed_Jerk_MM";


    var liste = [[tuple_1],[tuple_2],[tuple_4],[tuple_5],[tuple_6],[tuple_7],[tuple_8],[tuple_9],[tuple_10],[tuple_11]];
    var liste_str = liste.toString();   
    document.getElementById('liste_data').value = liste_str;
	document.getElementById('liste_data_f').submit();
}


function activate(colonne)
{   
    if (document.getElementById(colonne).value == 'on')
    {
        document.getElementById(colonne).value = 'off';
    }
    else
    {
        document.getElementById(colonne).value = 'on';
    }
}