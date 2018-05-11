/* C++ STL */
#include <iostream>


#include <stdio.h>
#include <math.h>
#include <iostream>
#include <fstream>
#include <cstdlib>
#include <sstream>
#include <string.h>
#include <ctime>
#include <vector>
#include <algorithm>


/* FNCS headers */
#include <fncs.hpp>
#include "CPP_PublishVar.hpp"

using namespace std; /* C++ standard namespace */

/* some C++ compilers have a nullptr instance,
 * otherwise we fall back to the old default of NULL */
#ifndef nullptr 
#define nullptr NULL
#endif

/* the current time of our simulator */
static fncs::time time_current=0;
/* time when sim will stop */
static fncs::time time_stop=10;

/* our simulator function, called by the main() function later */
static void generic_simulator(vector<string> &myKeys)
{




	// These are variables used to get and push values outside of FNCS
 	vector<string> SubscribedValues;
 	vector<string> SubscribedString; 
	string line;
	vector<double> myValues;

	/* ANDY'S CODE BEFORE START OF FNCS 

		BLA BLA BLA ---

	*/


	for(vector<int>::size_type i = 0; i != myKeys.size(); i+=2) {
		if (time_current < 5) {
			myValues.push_back(i*.01+60.00);
			myValues.push_back(i*0.01+68.00);	
		}
		else {
			myValues.push_back(i*.02+61.00);
			myValues.push_back(i*.02+69.00);	
		}
	}


	// THIS IS THE PORTION TO INITIALIZE FNCS 
	// ------START OF FNCS INITIALIZATION ---
	    fncs::time time_granted=0; 
	    fncs::time time_desired=0;

	    fncs::initialize();
	// ------END OF FNCS INITIALIZATION ---


    while (time_current < time_stop) {

	cout << "SimDERADC: Working Time is " << time_current << endl;


	/* THIS IS THE PORTION TO SUBSCRIBE VALUES FROM GRIDLABD 
	--------- VALUES ARE STORED IN SubscribedValues IN STRING ---
	--------- KEYS ARE STORED IN SubscribedString IN STRING ---
        --------- ONLY THE PUBLISHED MSG WILL BE SUBSCRIBED (NOT ALL) */  
        vector<string> events = fncs::get_events();
        for (vector<string>::iterator key=events.begin();
                key!=events.end(); ++key) {
	    SubscribedValues.push_back(fncs::get_value(*key));
	    SubscribedString.push_back(*key); 
            cout << "SimDERADC: received topic '"
                << *key
                << "' with value '"
                << fncs::get_value(*key)
                << "'"
                << endl;
        }

	/* ANDY'S CODE AFTER START OF FNCS
	! EXPECTED INPUTS: PARAMETERS FROM GRIDLABD
	! EXPECTED OUTPUT: PARAMETERS FOR PUBLICATION FOR GRIDLABD TO USE
	! NOTE THAT THIS PORTION SHOULD TALK TO MATLAB FUNCTIONS AS NEEDED, & TRACK TIMING SEPARATELY 
		If if (time_current==1){ Do something related to configuration AT THE BEGINNING}

		else {Regular computations FOR ALL THE SIMULATION STEPS}

	*/


	/* THIS IS THE PORTION TO PUBLISH VALUES FOR GRIDLABD OR ANY OTHER SIMULATOR 
	--------- VALUES ARE STORED IN myValues IN A DOUBLE VECTOR ---
	--------- KEYS ARE STORED IN myKeys IN A STRING VECTOR ---
        --------- PUBLISHED AT EACH SIMULATION TIME STEP UNLESS SPECIFIED OTHERWISWE */
	stringstream doubleToStringHeat, doubleToStringCool;
	for(vector<int>::size_type i = 0; i != myKeys.size(); i+=2) {
		doubleToStringHeat << myValues[i] ;
		doubleToStringCool << myValues[i+1] ;
		cout<<"Publication Keys are " << myKeys[i] << " and  " << myKeys[i] << endl;
		cout<<"Publication Values are " << doubleToStringHeat << " and  " << doubleToStringCool << endl;
		if (time_current<5) {
			fncs::publish(myKeys[i], doubleToStringHeat.str());
			fncs::publish(myKeys[i+1], doubleToStringCool.str());
		}
	
		else {
			fncs::publish(myKeys[i], doubleToStringHeat.str());
			fncs::publish(myKeys[i+1], doubleToStringCool.str());
		}
	
		doubleToStringCool.str(string());
		doubleToStringHeat.str(string());				
	}


	// TIME KEEPING OF FNCS 
	time_desired = time_current + 1;

        time_granted = fncs::time_request(time_desired);

        cout << "SimDERADC: time_request"
            << " current=" << time_current
            << " desired=" << time_desired
            << " granted=" << time_granted << endl;
        time_current = time_granted;


	// SOME SIMULATION END TASKS 
	 SubscribedValues.clear();
	 SubscribedString.clear();

    }

    // FINALIZATION OF FNCS 
    cout << "SimDERADC: DONE!" << endl;
    myValues.clear();

    fncs::finalize();
}


// A MAIN FUNCTION THAT CALLS OUR SIMULATOR FUNCTIONS
int main(int argc, char **argv)
{
    vector<string> myKeys;
    fill_myKeys(myKeys);

    try {
        cout << "starting generic simulator" << endl;
        generic_simulator(myKeys);

    } catch (const exception &e) {
        cout << e.what() << endl;
    }
    catch (const string &e) {
        cout << e << endl;
    }
    cout << "finished generic simulator" << endl;
    return 0;
}

