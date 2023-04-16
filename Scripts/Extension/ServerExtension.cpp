#include "Common.h"

#include "Server.h"

///# ...
///# param imageSlot ...
///# param imageName ...
///@ ExportMethod
[[maybe_unused]] void Server_Game_LoadImage(FOServer* self, int imageSlot, string_view imageName)
{
    UNUSED_VARIABLE(self);
    UNUSED_VARIABLE(imageSlot);
    UNUSED_VARIABLE(imageName);
}

///# ...
///# param imageSlot ...
///# param x ...
///# param y ...
///# return ...
///@ ExportMethod
[[maybe_unused]] uint Server_Game_GetImageColor(FOServer* self, int imageSlot, int x, int y)
{
    UNUSED_VARIABLE(self);
    UNUSED_VARIABLE(imageSlot);
    UNUSED_VARIABLE(x);
    UNUSED_VARIABLE(y);

    return 0;
}

///# ...
///# return ...
///@ ExportMethod
[[maybe_unused]] bool Server_Critter_IsFree(Critter* self)
{
    UNUSED_VARIABLE(self);

    return true;
}

///# ...
///# return ...
///@ ExportMethod
[[maybe_unused]] bool Server_Critter_IsBusy(Critter* self)
{
    UNUSED_VARIABLE(self);

    return false;
}

///# ...
///# param ms ...
///@ ExportMethod
[[maybe_unused]] void Server_Critter_Wait(Critter* self, uint ms)
{
    UNUSED_VARIABLE(self);
    UNUSED_VARIABLE(ms);
}
