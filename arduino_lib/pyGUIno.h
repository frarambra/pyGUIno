#include <Arduino.h>
#include "CmdMessenger.h"

enum available_commands{
	ack_start,
	request_pin, //PC will request a pin value, it will send it the value
	arduino_transmit_pin_value, //Arduino will transmit the pin int and the value
	request_debug_var_value, //PC will handle memory addr and tpye of a debug var value
	answer_debug_var_value, //Answer to the previous msg
	arduino_transmit_debug_var //Arduino will send to the pc a debug var
};

typedef enum{
	bool_var,
	byte_var,
	char_var,
	float_var,
	double_var,
	int_var,
	long_var,
	short_var,
	u_int_var,
	u_short_var,
	u_long_var
} data_type;


void attach_callbacks(CmdMessenger &cmd);

void on_request_pin(); // The pc will request a pin value

void send_debug_var_value();
void transmit_pin_value(int pin);

void add_update_debug_var(int data, bool var, const char name[]);
void add_update_debug_var(int data, byte var, const char name[]);
void add_update_debug_var(int data, char var, const char name[]);
void add_update_debug_var(int data, float var, const char name[]);
void add_update_debug_var(int data, double var, const char name[]);
void add_update_debug_var(int data, int var, const char name[]);
void add_update_debug_var(int data, long var, const char name[]);	
void add_update_debug_var(int data, short var, const char name[]);
void add_update_debug_var(int data, unsigned char var, const char name[]);
void add_update_debug_var(int data, unsigned int var, const char name[]);
void add_update_debug_var(int data, unsigned short var, const char name[]);
void add_update_debug_var(int data, unsigned long var, const char name[]);
