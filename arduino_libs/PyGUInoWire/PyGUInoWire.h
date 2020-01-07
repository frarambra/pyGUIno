#include <Wire.h>
#include "CmdMessenger.h"
#include "Arduino.h"
#include "PyGUIno.h"



//La clase no heredará de Wire, sino que esta clase será utilizada
//Como si fuera un atributo más
class PyGUInoWire {
	private:
		//Atributos
		CmdMessenger *cmd;
		
		
	public:
		//Atributos
		byte last_read_byte;
		uint16_t read_addr;
		uint16_t write_addr = 0;

		//Metodos

		PyGUInoWire(CmdMessenger &cmd); // Si hay una instacia de CmdMessenger la usaremos
		PyGUInoWire(); // En caso de no haber instancia la creamos
		void begin(int address); //OK
		void begin();
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

