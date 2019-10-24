/**
* Author: frarambra
* Website: https://github.com/frarambra
*
**/
#include "pyGUIno.h"
#include "CmdMessenger.h"
#include "Arduino.h"
#include "String.h"

// Constructor

pyGUIno::pyGUIno(CmdMessenger &cmdMessenger){
	pc_side = &cmdMessenger;
	
	//Initialize everything to zero
	for(debug_var tmp : list_debug_var){
		tmp.var_type = 0;
		tmp.ptr_var = 0x00;
		strcpy(tmp.id,"");
	}
	
}

//Utility functions
/*
	This function is designed to add a variable to track its values
	If the id is already taken it won't be added and return an error
	otherwise it will be added/updated the variable with the id
*/
int pyGUIno::add_debug_variable(data_types save_var, const char name[]){
	//Search by id
	if(strlen(name)>NAME_LIMIT)
		return -1;
		
	for(debug_var tmp : list_debug_var){
		if(!strcmp(tmp.id, name)){
			//Update and return
			
			return 0;
			
		}
	}
	//It means it hasn't been added to the debug_var_list
	//Add it and return 0
	
	

}

//Callback functions implementation

// TODO: Test function
void pyGUIno::on_add_track_pin(void){
	int i = 0;
	for(i=0; i < TOTAL_PIN; i++){
		pin_state[i] = pc_side->readBoolArg();
	}	
}

// TODO: Test function
void pyGUIno::on_stop_track_pin(void){
	int stop = pc_side->readInt16Arg(); // Number of remaining arguments to get
	int index;
	for (int i = 0; i < stop; i++){
		index = pc_side->readInt16Arg();
		pin_state[index] = false;
	}
}
	
	
void pyGUIno::on_get_debug_vars(void){
	//Send all the list of debug vars, just the id and the value
	
}
	
void pyGUIno::on_set_debug_var_value(void){
	//Get the addr of the var to set
	
	//Set the new value
	
}
	
void pyGUIno::notify_var_update(void){
	//It will send the new value of a var
}


// TODO: Test function
void pyGUIno::on_await_pins(void){
	int i;
	for(i = 0; i < TOTAL_PIN; i++){
		if(pin_state[i] && i <= TOTAL_DIGITAL_PIN){ //13
			pc_side->sendCmdStart(await_pins);
			pc_side->sendCmdArg(i);
			pc_side->sendCmdArg(digitalRead(i));
			pc_side->sendCmdEnd();
			
		}
		else if(pin_state[i] && i > TOTAL_DIGITAL_PIN){
			pc_side->sendCmdStart(await_pins);
			pc_side->sendCmdArg(i);
			pc_side->sendCmdArg(analogRead(i));
			pc_side->sendCmdEnd();
		}
	}
}

