/**
* Author: frarambra
* Website: https://github.com/frarambra
*
**/
#include "pyGUIno.h"
#include "CmdMessenger.h"
#include "Arduino.h"
#include "String.h"

CmdMessenger *pc_side;

//Tested, pc_side keeps the cmd address after function cast
void attach_callbacks(CmdMessenger &cmd){
	pc_side = &cmd;
	pc_side->attach(request_pin, on_request_pin);
	pc_side->attach(request_debug_var_value, send_debug_var_value);
	delay(500);
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

void add_update_debug_var(int data, void *addr, const char name[]){
	pc_side->sendCmdStart(arduino_transmit_debug_var);
	pc_side->sendCmdBinArg<int>(data);
	unsigned int tmp = (unsigned int) addr;
	pc_side->sendCmdBinArg<unsigned int>(tmp);
	pc_side->sendCmdArg(name);
	pc_side->sendCmdEnd();
}

void send_debug_var_value(){
	//We expect the variable address and type
	int data = pc_side->readBinArg<int>();
	unsigned int offset = pc_side->readBinArg<unsigned int>();
	char buff[100]; // Magic, yikes
	switch(data){
		case char_var:{
			char *value = (char *) offset;
			sprintf(buff, "%c", *value);
			break;
		}
		case float_var:{
			float *value = (float *)offset;
			dtostrf(*value, 15, 3, buff);
			break;
		}
		case bool_var:
		case byte_var:
		case int_var:{
			int *value = (int *)offset;
			sprintf(buff, "%d", *value);
			break;
		}
		case long_var:{
			long *value = (long *)offset;
			sprintf(buff, "%l", *value);
			break;
		}
		case short_var:{
			short *value = (short *)offset;
			sprintf(buff, "%d", *value);
			break;
		}
		case u_char_var:{
			unsigned char *value = (unsigned char *)offset;
			sprintf(buff, "%c", *value);
			break;
		}
		case u_int_var:{
			unsigned int *value = (unsigned int*)offset;
			sprintf(buff, "%u", *value);
			break;
		}
		case u_long_var:{
			unsigned long *value = (unsigned long *)offset;
			sprintf(buff, "%lu", *value);
			break;
		}
		default:{
			sprintf(buff, "error_type");
			break;
		}
	}
	pc_side->sendCmd(answer_debug_var_value, buff);
}
