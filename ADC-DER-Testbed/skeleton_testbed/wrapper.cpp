#include "MatlabDataArray.hpp"
#include "MatlabEngine.hpp"
#include <iostream>
#include <vector>

using matlab::data::Array;
using matlab::data::StructArray;
using matlab::data::TypedArray;
using matlab::data::ArrayFactory;

using std::cout;
using std::vector;
using std::unique_ptr;
using std::to_string;

#define matstr convertUTF8StringToUTF16String

void master() {

	using namespace matlab::engine;
    
	// Start MATLAB engine synchronously
	cout << "Starting MATLAB Engine... ";
    unique_ptr<MATLABEngine> mPtr = startMATLAB();
	cout << "Complete.\n";

	// Set up the population structures
	ArrayFactory af;

	// set up and run ADC domain approximation
	int numADC = 1;
	for ( int idxADC = 0 ; idxADC < numADC ; idxADC++ ) { 

		// electric water heaters
		// - heating_element_capacity[kW] -> prated[kW]
		cout << "Initializing water heaters... ";
		long unsigned int num_ewh = 1;
		StructArray ewh_pop 
				= af.createStructArray({1,num_ewh},{"name","prated"});
		for ( int idx = 0 ; idx < num_ewh ; idx++ ) {
			ewh_pop[idx]["name"] = af.createCharArray("EWH_"+to_string(idx));
			ewh_pop[idx]["prated"] = af.createScalar<double>(idx+1);
		}
		cout << "Complete.\n";
	
	
		// hvac systems -- note: powfac <- q = powfac * prated
		// ( ASSUME AIR CONDITONER ONLY )
		// - design_cooling_capacity[Btu/hr]*1[kw]/3412.0[Btu/hr] -> prated[kw]
		// ( ASSUME POWER FACTOR OF 0.85 )
		// - 0.6197 -> powfac
		cout << "Initializing HVAC systems... ";
		long unsigned int num_ac = 2;
		StructArray ac_pop
				= af.createStructArray({1,num_ac},{"name","prated","powfac"});
		for ( int idx = 0 ; idx < num_ac ; idx++ ) {
			ac_pop[idx]["name"] = af.createCharArray("HVAC_"+to_string(idx));
			ac_pop[idx]["prated"] = af.createScalar<double>(idx+1);
			ac_pop[idx]["powfac"] = af.createScalar<double>(0.3);
		}
		cout << "Complete.\n";
	
		// batteries
		// - batt.rated_power -> prated
		// - Binv.rated_power -> invcap
		cout << "Initializing batteries... ";
		long unsigned int num_batt = 3;
		StructArray batt_pop 
				= af.createStructArray({1,num_batt},{"name","prated","invcap"});
		for ( int idx = 0 ; idx < num_batt ; idx++ ) {
			batt_pop[idx]["name"] = af.createCharArray("batt_"+to_string(idx));
			batt_pop[idx]["prated"] = af.createScalar<double>(idx+1);
			batt_pop[idx]["invcap"] = af.createScalar<double>(idx+1);
		}
		cout << "Complete.\n";
	
		// photovoltaics
		// ( Assume that curtailment only affects inverter output )
		// - abs{solar.VA_Out} -> pgenmax
		// - solar.rated_power -> invcap
		cout << "Initializing photovoltaics... ";
		long unsigned int num_pv = 4;
		StructArray pv_pop 
					= af.createStructArray({1,num_pv},{"name","pgenmax","invcap"});
		for	( int idx = 0 ; idx < num_pv ; idx++ ) {
				pv_pop[idx]["name"] = af.createCharArray("PV_"+to_string(idx));
			pv_pop[idx]["pgenmax"] = af.createScalar<double>(idx+1);
			pv_pop[idx]["invcap"] = af.createScalar<double>(idx+1);
		}
		cout << "Complete.\n";
	
	
		// Run task 2.1 ADC domain approximation
		// approximate the domain
		mPtr->eval(matstr("help matlab.basic_2_1"));
	    cout << "Running ADC domain approximation...\n";
		vector<Array> dom_inputs = {ewh_pop,ac_pop,batt_pop,pv_pop};
		vector<Array> result = mPtr->feval(matstr("matlab.basic_2_1"),2,dom_inputs);
		TypedArray<double> Fout_adc(result[0]);
		TypedArray<double> Dout_adc(result[1]);
	
		// Print results
		for ( auto idx = 0 ; idx < Dout_adc.getNumberOfElements() ; idx++ )
			cout << to_string(Fout_adc[idx][0]) + "x + " 
					+ to_string(Fout_adc[idx][1]) + " <= " 
					+ to_string(Dout_adc[idx]) + "\n";
		cout << "ADC domain approximation Complete.\n";
	}

	// Emulate the PFO
	double Popt = 0, Qopt = 0;

	// Determine the midpoint of the flex. region and send that to 2.4
	for ( int idxADC = 0 ; idxADC < numADC ; idxADC++ ) {
	}


	// Run task 2.4 ADC dispatch function
	for ( int idxADC = 0 ; idxADC < numADC ; idxADC++ ) {

	}

}

int main() {
	cout << "Starting ADC wrapper.\n";
    master();
    return 0;
}
