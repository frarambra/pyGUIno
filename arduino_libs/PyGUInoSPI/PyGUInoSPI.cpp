#include "Arduino.h"
#include "pyGUInoSPI.h"
#include "CmdMessenger.h"


PyGUInoSPI::PyGUInoSPI(CmdMessenger &cmd){
	this->cmd = &cmd;
}

void PyGUInoSPI::begin(){
	SPI.begin();
}

void PyGUInoSPI::end(){
	SPI.end();
}

void PyGUInoSPI::beginTransaction(SPISettings settings){
	SPI.beginTransaction(settings);
}

void PyGUInoSPI::endTransaction(){
	SPI.endTransaction();
}

uint8_t PyGUInoSPI::transfer(uint8_t value){
	uint8_t retorno;
	uint16_t tmp;
	
	cmd->sendCmdStart(arduino_spi_transfer);
	tmp = (uint16_t) value;
	cmd->sendCmdBinArg<uint16_t>(tmp);
	retorno = SPI.transfer(value);
	tmp = (uint16_t) retorno;
	cmd->sendCmdBinArg<uint16_t>(tmp);
	cmd->sendCmdEnd();
	
	return retorno;
}

uint16_t PyGUInoSPI::transfer16(uint16_t value){
	
	uint16_t tmp;
	cmd->sendCmdStart(arduino_spi_transfer);
	cmd->sendCmdBinArg<uint16_t>(value);
	tmp = SPI.transfer(value);
	cmd->sendCmdBinArg<uint16_t>(tmp);
	cmd->sendCmdEnd();
	
	return tmp;
}

byte PyGUInoSPI::read(){
	uint16_t tmp = (uint16_t) 0;
	cmd->sendCmdStart(arduino_spi_transfer);
	cmd->sendCmdBinArg<uint16_t>(tmp); // Tx
	tmp = (uint16_t) SPDR;
	cmd->sendCmdBinArg<uint16_t>(tmp);
	cmd->sendCmdEnd();
	
	return tmp;
}



void PyGUInoSPI::transfer(void *buff, size_t count){
	//A implementar
	SPI.transfer(buff, count);
}


void PyGUInoSPI::usingInterrupt(int interruptNumber){
	SPI.usingInterrupt(interruptNumber);
}

void PyGUInoSPI::setClockDivider(int clock_divider){
	SPI.setClockDivider(clock_divider);
}