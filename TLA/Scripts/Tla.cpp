#include "fonline_tla.h"

// Slot/parameters allowing
EXPORT bool anyExport( uint8, Item &, Critter &, Critter & toCr );

// Initialization

// In this functions (DllMain and DllLoad) all global variables is NOT initialized, use FONLINE_DLL_ENTRY instead
#if defined ( FO_WINDOWS )
int __stdcall DllMain( void* module, unsigned long reason, void* reserved ) { return 1; }
#elif defined ( FO_LINUX )
void __attribute__( ( constructor ) ) DllLoad()   {}
void __attribute__( ( destructor ) )  DllUnload() {}
#endif

FONLINE_DLL_ENTRY( isCompiler )
{}

// Slot/parameters allowing

EXPORT bool anyExport( uint8, Item&, Critter&, Critter& toCr )
{
    return false;
}
