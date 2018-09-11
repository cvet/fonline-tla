#include "fonline_tla.h"

// Entry point
FONLINE_DLL_ENTRY( isCompiler )
{
    if( isCompiler )
        return;

    // Test Memory Level 3 for loaded DLLs
    for( uint i = 0; i < 666; i++ )
        volatile char* leak = new char[ 2 ];
}

// Test function
EXPORT void TestFunc( ScriptString& str )
{
    Log( "TEST %s", str.c_str() );
}

EXPORT bool TestScriptCallNative( ScriptString& moduleName, ScriptString& funcDecl )
{
    uint bindId = FOnline->ScriptBind( moduleName.c_str(), funcDecl.c_str(), true );
    if( bindId && FOnline->ScriptPrepare( bindId ) )
    {
        FOnline->ScriptSetArgInt( 321 );
        FOnline->ScriptSetArgUInt64( 2222222 );
        FOnline->ScriptSetArgFloat( 1.55f );
        FOnline->ScriptSetArgObject( &funcDecl );
        if( FOnline->ScriptRunPrepared() )
        {
            Log( "TestScriptCallNative return %g.\n", FOnline->ScriptGetReturnedUInt64() );
            return true;
        }
    }
    return false;
}

EXPORT void StringExample()
{
    ScriptString& str = ScriptString::Create( "Test1" );
    Log( "StringExample 1: '%s' (len %u, ref count %d)\n", str.c_str(), str.length(), str.rcount() );
    str = "Hello World!";
    Log( "StringExample 2: '%s' (len %u, ref count %d)\n", str.c_str(), str.length(), str.rcount() );
    ScriptString& str2 = ScriptString::Create();
    ScriptString& str3 = ScriptString::Create();
    str2 = str3;
    str = "1234567890abcdefghijklmnopqrs....";
    Log( "StringExample 3: '%s' (len %u, ref count %d)\n", str.c_str(), str.length(), str.rcount() );
    str.Release();
    str2.Release();
    str3.Release();
}

EXPORT void ArrayExample()
{
    ScriptArray&  arr = ScriptArray::Create( "string" );
    ScriptString& first = ScriptString::Create( "first" );
    arr.InsertFirst( &first );
    first.Release();
    arr.InsertAt( 1, &ScriptString::Create( "mid" ) );    // Leak
    arr.InsertLast( &ScriptString::Create( "last" ) );    // Leak
    arr.InsertFirst( &ScriptString::Create( "first0" ) ); // Leak
    arr.RemoveAt( 0 );
    Log( "Array example:\n" );
    for( asUINT i = 0; i < arr.GetSize(); i++ )
    {
        ScriptString& str = *(ScriptString*) arr.At( i );
        Log( "%u) '%s'\n", i, str.c_str() );
    }
    arr.Release();
}
