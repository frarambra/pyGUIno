#include <Arduino.h>
#include "CmdMessenger.h"
#define TOTAL_ANALOGIC_PIN 6
#define TOTAL_DIGITAL_PIN 13
#define TOTAL_PIN TOTAL_DIGITAL_PIN + TOTAL_ANALOGIC_PIN
#define MAX_DEBUG 30
#define NAME_LIMIT 10


typedef struct{
	int var_type; //Data type will be assigned by an integer as an id
 	void *ptr_var;
 	char id[NAME_LIMIT]; // In order to allow the user to recognize the variable on the pc
} debug_var;

typedef enum{bool_var,
			byte_var,
			char_var,
			double_var,
			float_var,
			int_var,
			long_var,
			short_var,
			u_char_var,
			u_int_var,
			u_long_var
} data_types;
	
/**
* 
* Aqui debe venir la definicion del "esqueleto de la clase"
* declaracion de los atributos y metodos que contrendra,
* asi como su visibilidad
* 
**/

class pyGUIno{
	private:
		enum available_commands{ 
			add_track_pin,
			stop_track_pin,
			get_debug_vars,
			set_debug_var_value,
			await_pins
		} commands;
				
		debug_var list_debug_var[MAX_DEBUG];
		int pin_state[TOTAL_PIN]; // By default zero
		CmdMessenger *pc_side;

	public:
		pyGUIno(CmdMessenger &cmdMessenger);
		//Callbacks
		void on_add_track_pin(void);
		void on_stop_track_pin(void);
		void on_await_pins(void);
		void on_get_debug_vars(void);
		void on_set_debug_var_value(void);
		void notify_var_update(void);
		//Utilities
		int add_debug_variable(data_types save_var, const char name[]);
};
