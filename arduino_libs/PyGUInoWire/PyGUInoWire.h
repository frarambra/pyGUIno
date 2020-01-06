#include <Wire.h>
#include "CmdMessenger.h"
#include "Arduino.h"

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
	arduino_byte_write_i2c
	//Avisa al ordenador de que se envia uno o más bytes 
	// addr, bytes
};


//La clase no heredará de Wire, sino que esta clase será utilizada
//Como si fuera un atributo más
class PyGUInoWire {
	private:
		//Atributes 
		CmdMessenger *cmd;
		byte last_read_byte;
		int read_addr;
		int write_addr;
		
		//Methods
	public:
		PyGUInoWire(CmdMessenger &cmd); // Si hay una instacia de CmdMessenger la usaremos
		PyGUInoWire(); // En caso de no haber instancia la creamos
		void begin(int address); //OK
		byte requestFrom(int address, int quantity);//OK
		byte requestFrom(int address, int quantity, bool stop);//OK
		void beginTransmission(int address);//OK
		byte endTransmission(); 		// 0 ok; 1 data too long to fit in transmit buffer
		byte endTransmission(bool stop);// 2 recieved NACK on transmit of addres, 3 recv NACK on transmit data
										// 4 other error
		byte write(byte value);//OK
		byte write(const char name[]);//OK
		byte write(byte data[], int length);//OK
		byte available();//OK
		byte read();//OK
		void SetClock(int clockFrequency);
		//void onReceive(void (*function)(int));//Ni idea de como hacer la sintaxis
		void onRequest(void (*function)(void));//ok
};
