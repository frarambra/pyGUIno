#include <Arduino.h>
#include <SPI.h>
#include "CmdMessenger.h"


//Mensajes definidos entre el ordenador y Arduino
enum available_commands{
	ack_start,
	request_pin, //PC will request a pin value, it will send it the value
	arduino_transmit_pin_value, //Arduino will transmit the pin int and the value
	request_debug_var_value, //PC will handle memory addr and tpye of a debug var value
	answer_debug_var_value, //Answer to the previous msg
	arduino_transmit_debug_var, //Arduino will send to the pc a debug var
	// Solo nos interesa avisar de bytes entrantes y salientes
	arduino_byte_read_i2c,
	//Avisa al ordenador de que se ha leido un byte junto con la direccion que lo envio
	// addr, byte
	arduino_byte_write_i2c,
	//Avisa al ordenador de que se envia uno o más bytes 
	// addr, bytes
	arduino_spi_transfer
	//Debe serán o 16 bits o 32, con enviar dos uint16_t valdría  
	// primero lo que Arduino enviará luego lo que Arduino a recibido
};

class PyGUInoSPI {
	private:
		CmdMessenger *cmd;
		
	public:
		PyGUInoSPI(CmdMessenger &cmd);
		void begin();
		void end();
		void beginTransaction(SPISettings settings);
		void endTransaction();
		uint8_t transfer(uint8_t value);//
		void transfer(void *buff, size_t count); //Parece que deja en buff el dato
		uint16_t transfer16(uint16_t value);
		void usingInterrupt(int interruptNumber);
		
		
};
