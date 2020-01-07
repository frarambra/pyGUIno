#include "Arduino.h"
#include "CmdMessenger.h"
#include "PyGUInoWire.h"


PyGUInoWire::PyGUInoWire(CmdMessenger &cmd){
	this->cmd = &cmd;
	this->cmd->sendCmd(ack_start, "Arduino has booted");	

}

// Metodos que me asignan los valores de los atributos
// write_addr y read_addr
void PyGUInoWire::beginTransmission(int address){
	write_addr = (uint16_t) address;
	Wire.beginTransmission(address);
}

byte PyGUInoWire::requestFrom(int address, int quantity){
	read_addr = (uint16_t) address;
	return Wire.requestFrom(address, quantity);
}

byte PyGUInoWire::requestFrom(int address, int quantity, bool stop){
	read_addr = (uint16_t) address;
	return Wire.requestFrom(address, quantity, stop);
}

byte PyGUInoWire::write(byte value){
	cmd->sendCmdStart(arduino_byte_write_i2c);
	cmd->sendCmdBinArg<uint16_t>(write_addr);
	cmd->sendCmdBinArg<byte>(value);
	cmd->sendCmdEnd();
	return Wire.write(value);
}

byte PyGUInoWire::write(const char data[]){
	
	int i = 0;
	cmd->sendCmdStart(arduino_byte_write_i2c);
	cmd->sendCmdBinArg<uint16_t>(write_addr);
	while(data[i]!='\0'){
		cmd->sendCmdBinArg<byte>(data[i]);
		i++;
	}
	cmd->sendCmdEnd();
	
	return Wire.write(data);
}

byte PyGUInoWire::write(byte data[], int length){
	
	int i = 0;
	cmd->sendCmdStart(arduino_byte_write_i2c);
	cmd->sendCmdBinArg<uint16_t>(write_addr);
	while(i<length){
		cmd->sendCmdBinArg<byte>(data[i]);
		i++;
	}
	cmd->sendCmdEnd();
	
	return Wire.write(data, length);
}

byte PyGUInoWire::read(){
	
	//Solo tenemos que devolver el byte leido, lo ideal sería tambien dar
	//La direccion del periferico que lo hace
	cmd->sendCmdStart(arduino_byte_read_i2c);
	cmd->sendCmdBinArg<uint16_t>(write_addr);//addr
	byte tmp = Wire.read();
	cmd->sendCmdBinArg<byte>(tmp);		//value
	cmd->sendCmdEnd();
	return tmp;
}

//Resto del archivo es basura para hacer patron fachada

void PyGUInoWire::begin(int address){
	address ? Wire.begin(address) : Wire.begin();
}

void PyGUInoWire::begin(){
	Wire.begin();
}

byte PyGUInoWire::endTransmission(){
	return Wire.endTransmission();
}

byte PyGUInoWire::endTransmission(bool stop){
	return Wire.endTransmission(stop);
}



byte PyGUInoWire::available(){
	return Wire.available();
}



void PyGUInoWire::SetClock(int clockFrequency){
	Wire.setClock(clockFrequency);
}

//void PyGUInoWire::onReceive(void (*function)(int)){
//	Wire.onReceive((*function)(int));
//}

void PyGUInoWire::onRequest(void (*function)(void)){
	Wire.onRequest(function);
}

