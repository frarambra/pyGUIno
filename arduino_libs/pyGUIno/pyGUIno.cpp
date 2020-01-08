/**
* Author: frarambra
* Website: https://github.com/frarambra
*
**/

#include "PyGUIno.h"
#include "CmdMessenger.h"
#include "Arduino.h"

CmdMessenger *pc_side;

//Tested, pc_side keeps the cmd address after function cast
void attach_callbacks(CmdMessenger &cmd){
	pc_side = &cmd;
	pc_side->attach(request_pin, on_request_pin);
	pc_side->attach(request_debug_var_value, send_debug_var_value);
	delay(5000);
	pc_side->sendCmd(ack_start, "Arduino has booted");	
}

void transmit_pin_value(int pin){
	pc_side->sendCmdStart(arduino_transmit_pin_value);
	pc_side->sendCmdBinArg<int>(pin);
	int value = (pin < A0) ? digitalRead(pin) : analogRead(pin);
	pc_side->sendCmdBinArg<int>(value);
	pc_side->sendCmdEnd();
}

void on_request_pin(){
	int pin = pc_side->readBinArg<int>();
	int value = (pin < A0) ? digitalRead(pin) : analogRead(pin);
	pc_side->sendBinCmd(request_pin, value);
}

void actual_add_update(int data, int offset, void *addr, const char name[]){
	pc_side->sendCmdStart(arduino_transmit_debug_var);
	pc_side->sendCmdBinArg<int>(data); //Data type
	unsigned int tmp = (unsigned int) addr;
	pc_side->sendCmdBinArg<unsigned int>(tmp); //Addr
	pc_side->sendCmdArg(name); //Name
	for(int i=0; i< offset; i++){
		byte *tmp = (byte *)addr;
		pc_side->sendCmdBinArg<byte>(*tmp);// Bunch of bytes containing the value
		addr++;
	}
	pc_side->sendCmdEnd();
}

void add_update_debug_var(int data, bool var, const char name[]){
	actual_add_update(data, sizeof(var), &var, name);
}

void add_update_debug_var(int data, byte var, const char name[]){
	actual_add_update(data, sizeof(var), &var, name);
}

void add_update_debug_var(int data, char var, const char name[]){
	actual_add_update(data, sizeof(var), &var, name);
}

void add_update_debug_var(int data, float var, const char name[]){
	actual_add_update(data, sizeof(var), &var, name);
}

void add_update_debug_var(int data, double var, const char name[]){
	actual_add_update(data, sizeof(var), &var, name);
}

void add_update_debug_var(int data, int var, const char name[]){
	actual_add_update(data, sizeof(var), &var, name);
}

void add_update_debug_var(int data, long var, const char name[]){
	actual_add_update(data, sizeof(var), &var, name);
}	

void add_update_debug_var(int data, short var, const char name[]){
	actual_add_update(data, sizeof(var), &var, name);
}

void add_update_debug_var(int data, unsigned int var, const char name[]){
	actual_add_update(data, sizeof(var), &var, name);
}

void add_update_debug_var(int data, unsigned short var, const char name[]){
	actual_add_update(data, sizeof(var), &var, name);
}

void add_update_debug_var(int data, unsigned long var, const char name[]){
	actual_add_update(data, sizeof(var), &var, name);
}

void send_debug_var_value(){
	//We expect the variable address and type
	int offset = pc_side->readBinArg<int>();
	unsigned int tmp = pc_side->readBinArg<unsigned int>();
	byte *addr = (byte *) tmp;
	pc_side->sendCmdStart(answer_debug_var_value);
	for(int i=0; i< offset; i++){
		pc_side->sendCmdBinArg<byte>(*addr);
		addr++;
	}
	pc_side->sendCmdEnd();
	//TODO: testing the function

}

