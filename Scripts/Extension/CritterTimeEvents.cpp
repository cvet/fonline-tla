#include "Common.h"

#include "Server.h"

// ReSharper disable CppInconsistentNaming

///@ Property Critter PrivateServer hstring[] TE_FuncName
///@ Property Critter PrivateServer uint[] TE_Rate
///@ Property Critter PrivateServer uint[] TE_NextTime
///@ Property Critter PrivateServer int[] TE_Identifier

/*
    void AddCrTimeEvent(hstring func_num, uint rate, uint duration, int identifier) const;
    void EraseCrTimeEvent(int index);
    void ContinueTimeEvents(int offs_time);

    // Internal misc/drugs time events
    // One event per cycle
    / *if (cr->IsNonEmptyTE_FuncNum())
    {
        CScriptArray* te_next_time = cr->GetTE_NextTime();
        uint next_time = *(uint*)te_next_time->At(0);
        if (!next_time || GameTime.GetFullSecond() >= next_time)
        {
            CScriptArray* te_func_num = cr->GetTE_FuncNum();
            CScriptArray* te_rate = cr->GetTE_Rate();
            CScriptArray* te_identifier = cr->GetTE_Identifier();
            RUNTIME_ASSERT(te_next_time->GetSize() == te_func_num->GetSize());
            RUNTIME_ASSERT(te_func_num->GetSize() == te_rate->GetSize());
            RUNTIME_ASSERT(te_rate->GetSize() == te_identifier->GetSize());
            hash func_num = *(hash*)te_func_num->At(0);
            uint rate = *(hash*)te_rate->At(0);
            int identifier = *(hash*)te_identifier->At(0);
            te_func_num->Release();
            te_rate->Release();
            te_identifier->Release();

            cr->EraseCrTimeEvent(0);

            uint time = GetTimeMultiplier() * 1800; // 30 minutes on error
            ScriptSys.PrepareScriptFuncContext(func_num, cr->GetName());
            ScriptSys.SetArgEntity(cr);
            ScriptSys.SetArgUInt(identifier);
            ScriptSys.SetArgAddress(&rate);
            if (ScriptSys.RunPrepared())
                time = ScriptSys.GetReturnedUInt();
            if (time)
                cr->AddCrTimeEvent(func_num, rate, time, identifier);
        }
        te_next_time->Release();
    }* /

void Critter::AddCrTimeEvent(hstring / *func_num* /, uint / *rate* /, uint duration, int / *identifier* /) const
{
    // if (duration != 0u) {
    //    duration += _gameTime.GetFullSecond();
    //}

    / *CScriptArray* te_next_time = GetTE_NextTime();
    CScriptArray* te_func_num = GetTE_FuncNum();
    CScriptArray* te_rate = GetTE_Rate();
    CScriptArray* te_identifier = GetTE_Identifier();
    RUNTIME_ASSERT(te_next_time->GetSize() == te_func_num->GetSize());
    RUNTIME_ASSERT(te_func_num->GetSize() == te_rate->GetSize());
    RUNTIME_ASSERT(te_rate->GetSize() == te_identifier->GetSize());

    uint i = 0;
    for (uint j = te_func_num->GetSize(); i < j; i++)
        if (duration < *(uint*)te_next_time->At(i))
            break;

    te_next_time->InsertAt(i, &duration);
    te_func_num->InsertAt(i, &func_num);
    te_rate->InsertAt(i, &rate);
    te_identifier->InsertAt(i, &identifier);

    SetTE_NextTime(te_next_time);
    SetTE_FuncNum(te_func_num);
    SetTE_Rate(te_rate);
    SetTE_Identifier(te_identifier);

    te_next_time->Release();
    te_func_num->Release();
    te_rate->Release();
    te_identifier->Release();* /
}

void Critter::EraseCrTimeEvent(int index)
{
    / *CScriptArray* te_next_time = GetTE_NextTime();
    CScriptArray* te_func_num = GetTE_FuncNum();
    CScriptArray* te_rate = GetTE_Rate();
    CScriptArray* te_identifier = GetTE_Identifier();
    RUNTIME_ASSERT(te_next_time->GetSize() == te_func_num->GetSize());
    RUNTIME_ASSERT(te_func_num->GetSize() == te_rate->GetSize());
    RUNTIME_ASSERT(te_rate->GetSize() == te_identifier->GetSize());

    if (index < (int)te_next_time->GetSize())
    {
        te_next_time->RemoveAt(index);
        te_func_num->RemoveAt(index);
        te_rate->RemoveAt(index);
        te_identifier->RemoveAt(index);

        SetTE_NextTime(te_next_time);
        SetTE_FuncNum(te_func_num);
        SetTE_Rate(te_rate);
        SetTE_Identifier(te_identifier);
    }

    te_next_time->Release();
    te_func_num->Release();
    te_rate->Release();
    te_identifier->Release();* /
}

void Critter::ContinueTimeEvents(int offs_time) {
    / *CScriptArray* te_next_time = GetTE_NextTime();
    if (te_next_time->GetSize() > 0)
    {
        for (uint i = 0, j = te_next_time->GetSize(); i < j; i++)
            *(uint*)te_next_time->At(i) += offs_time;

        SetTE_NextTime(te_next_time);
    }
    te_next_time->Release();* /
}
*/

/// NativeEntry
[[maybe_unused]] void Server_InitCritterTimeEvents(FOServer* self)
{
}

///# ...
///# param func ...
///# param duration ...
///# param identifier ...
///# return ...
///@ ExportMethod
[[maybe_unused]] void Server_Critter_AddTimeEvent(Critter* self, ScriptFuncName<uint, Critter, int, uint&> func, uint duration, int identifier)
{
    /*hstring func_num = self->GetEngine()->ScriptSys.BindScriptFuncNumByFunc(func);
    if (!func_num)
        throw ScriptException("Function not found");

    self->AddCrTimeEvent(func_num, 0, duration, identifier);*/
}

///# ...
///# param func ...
///# param duration ...
///# param identifier ...
///# param rate ...
///# return ...
///@ ExportMethod
[[maybe_unused]] void Server_Critter_AddTimeEvent(Critter* self, ScriptFuncName<uint, Critter, int, uint&> func, uint duration, int identifier, uint rate)
{
    /*hstring func_num = self->GetEngine()->ScriptSys.BindScriptFuncNumByFunc(func);
    if (!func_num)
        throw ScriptException("Function not found");

    self->AddCrTimeEvent(func_num, rate, duration, identifier);*/
}

///# ...
///# param identifier ...
///# param indexes ...
///# param durations ...
///# param rates ...
///# return ...
///@ ExportMethod
[[maybe_unused]] uint Server_Critter_GetTimeEvents(Critter* self, int identifier, vector<uint>& indexes, vector<uint>& durations, vector<uint>& rates)
{
    /*CScriptArray* te_identifier = self->GetTE_Identifier();
    UIntVec te_vec;
    for (uint i = 0, j = te_identifier->GetSize(); i < j; i++)
    {
        if (*(int*)te_identifier->At(i) == identifier)
            te_vec.push_back(i);
    }
    te_identifier->Release();

    uint size = (uint)te_vec.size();
    if (!size || (!indexes && !durations && !rates))
        return size;

    CScriptArray* te_next_time = nullptr;
    CScriptArray* te_rate = nullptr;

    uint indexes_size = 0, durations_size = 0, rates_size = 0;
    if (indexes)
    {
        indexes_size = indexes->GetSize();
        indexes->Resize(indexes_size + size);
    }
    if (durations)
    {
        te_next_time = self->GetTE_NextTime();
        RUNTIME_ASSERT(te_next_time->GetSize() == te_identifier->GetSize());
        durations_size = durations->GetSize();
        durations->Resize(durations_size + size);
    }
    if (rates)
    {
        te_rate = self->GetTE_Rate();
        RUNTIME_ASSERT(te_rate->GetSize() == te_identifier->GetSize());
        rates_size = rates->GetSize();
        rates->Resize(rates_size + size);
    }

    for (uint i = 0; i < size; i++)
    {
        if (indexes)
        {
            *(uint*)indexes->At(indexes_size + i) = te_vec[i];
        }
        if (durations)
        {
            uint next_time = *(uint*)te_next_time->At(te_vec[i]);
            *(uint*)durations->At(durations_size + i) =
                (next_time > self->GetEngine()->Settings.FullSecond ? next_time - self->GetEngine()->Settings.FullSecond : 0);
        }
        if (rates)
        {
            *(uint*)rates->At(rates_size + i) = *(uint*)te_rate->At(te_vec[i]);
        }
    }

    if (te_next_time)
        te_next_time->Release();
    if (te_rate)
        te_rate->Release();

    return size;*/
    return 0;
}

///# ...
///# param findIdentifiers ...
///# param identifiers ...
///# param indexes ...
///# param durations ...
///# param rates ...
///# return ...
///@ ExportMethod
[[maybe_unused]] uint Server_Critter_GetTimeEvents(Critter* self, const vector<int>& findIdentifiers, const vector<int>& identifiers, vector<uint>& indexes, vector<uint>& durations, vector<uint>& rates)
{
    /*IntVec find_vec;
    self->GetEngine()->ScriptSys.AssignScriptArrayInVector(find_vec, findIdentifiers);

    CScriptArray* te_identifier = self->GetTE_Identifier();
    UIntVec te_vec;
    for (uint i = 0, j = te_identifier->GetSize(); i < j; i++)
    {
        if (std::find(find_vec.begin(), find_vec.end(), *(int*)te_identifier->At(i)) != find_vec.end())
            te_vec.push_back(i);
    }

    uint size = (uint)te_vec.size();
    if (!size || (!identifiers && !indexes && !durations && !rates))
    {
        te_identifier->Release();
        return size;
    }

    CScriptArray* te_next_time = nullptr;
    CScriptArray* te_rate = nullptr;

    uint identifiers_size = 0, indexes_size = 0, durations_size = 0, rates_size = 0;
    if (identifiers)
    {
        identifiers_size = identifiers->GetSize();
        identifiers->Resize(identifiers_size + size);
    }
    if (indexes)
    {
        indexes_size = indexes->GetSize();
        indexes->Resize(indexes_size + size);
    }
    if (durations)
    {
        te_next_time = self->GetTE_NextTime();
        RUNTIME_ASSERT(te_next_time->GetSize() == te_identifier->GetSize());
        durations_size = durations->GetSize();
        durations->Resize(durations_size + size);
    }
    if (rates)
    {
        te_rate = self->GetTE_Rate();
        RUNTIME_ASSERT(te_rate->GetSize() == te_identifier->GetSize());
        rates_size = rates->GetSize();
        rates->Resize(rates_size + size);
    }

    for (uint i = 0; i < size; i++)
    {
        if (identifiers)
        {
            *(int*)identifiers->At(identifiers_size + i) = *(uint*)te_identifier->At(te_vec[i]);
        }
        if (indexes)
        {
            *(uint*)indexes->At(indexes_size + i) = te_vec[i];
        }
        if (durations)
        {
            uint next_time = *(uint*)te_next_time->At(te_vec[i]);
            *(uint*)durations->At(durations_size + i) =
                (next_time > self->GetEngine()->Settings.FullSecond ? next_time - self->GetEngine()->Settings.FullSecond : 0);
        }
        if (rates)
        {
            *(uint*)rates->At(rates_size + i) = *(uint*)te_rate->At(te_vec[i]);
        }
    }

    te_identifier->Release();
    if (te_next_time)
        te_next_time->Release();
    if (te_rate)
        te_rate->Release();

    return size;*/
    return 0;
}

///# ...
///# param index ...
///# param newDuration ...
///# param newRate ...
///@ ExportMethod
[[maybe_unused]] void Server_Critter_ChangeTimeEvent(Critter* self, uint index, uint newDuration, uint newRate)
{
    /*CScriptArray* te_func_num = self->GetTE_FuncNum();
    CScriptArray* te_identifier = self->GetTE_Identifier();
    RUNTIME_ASSERT(te_func_num->GetSize() == te_identifier->GetSize());
    if (index >= te_func_num->GetSize())
    {
        te_func_num->Release();
        te_identifier->Release();
        throw ScriptException("Index arg is greater than maximum time events");
    }

    hstring func_num = *(hash*)te_func_num->At(index);
    int identifier = *(int*)te_identifier->At(index);
    te_func_num->Release();
    te_identifier->Release();

    self->EraseCrTimeEvent(index);
    self->AddCrTimeEvent(func_num, newRate, newDuration, identifier);*/
}

///# ...
///# param index ...
///@ ExportMethod
[[maybe_unused]] void Server_Critter_EraseTimeEvent(Critter* self, uint index)
{
    /*CScriptArray* te_func_num = self->GetTE_FuncNum();
    uint size = te_func_num->GetSize();
    te_func_num->Release();
    if (index >= size)
        throw ScriptException("Index arg is greater than maximum time events");

    self->EraseCrTimeEvent(index);*/
}

///# ...
///# param identifier ...
///# return ...
///@ ExportMethod
[[maybe_unused]] uint Server_Critter_EraseTimeEvents(Critter* self, int identifier)
{
    /*CScriptArray* te_next_time = self->GetTE_NextTime();
    CScriptArray* te_func_num = self->GetTE_FuncNum();
    CScriptArray* te_rate = self->GetTE_Rate();
    CScriptArray* te_identifier = self->GetTE_Identifier();
    RUNTIME_ASSERT(te_next_time->GetSize() == te_func_num->GetSize());
    RUNTIME_ASSERT(te_func_num->GetSize() == te_rate->GetSize());
    RUNTIME_ASSERT(te_rate->GetSize() == te_identifier->GetSize());

    uint result = 0;
    for (uint i = 0; i < te_identifier->GetSize();)
    {
        if (identifier == *(int*)te_identifier->At(i))
        {
            result++;
            te_next_time->RemoveAt(i);
            te_func_num->RemoveAt(i);
            te_rate->RemoveAt(i);
            te_identifier->RemoveAt(i);
        }
        else
        {
            i++;
        }
    }

    self->SetTE_NextTime(te_next_time);
    self->SetTE_FuncNum(te_func_num);
    self->SetTE_Rate(te_rate);
    self->SetTE_Identifier(te_identifier);

    te_next_time->Release();
    te_func_num->Release();
    te_rate->Release();
    te_identifier->Release();

    return result;*/
    return 0;
}

///# ...
///# param identifiers ...
///# return ...
///@ ExportMethod
[[maybe_unused]] uint Server_Critter_EraseTimeEvents(Critter* self, const vector<int>& identifiers)
{
    /*IntVec identifiers_;
    self->GetEngine()->ScriptSys.AssignScriptArrayInVector(identifiers_, identifiers);

    CScriptArray* te_next_time = self->GetTE_NextTime();
    CScriptArray* te_func_num = self->GetTE_FuncNum();
    CScriptArray* te_rate = self->GetTE_Rate();
    CScriptArray* te_identifier = self->GetTE_Identifier();
    RUNTIME_ASSERT(te_next_time->GetSize() == te_func_num->GetSize());
    RUNTIME_ASSERT(te_func_num->GetSize() == te_rate->GetSize());
    RUNTIME_ASSERT(te_rate->GetSize() == te_identifier->GetSize());

    uint result = 0;
    for (uint i = 0; i < te_func_num->GetSize();)
    {
        if (std::find(identifiers_.begin(), identifiers_.end(), *(int*)te_identifier->At(i)) != identifiers_.end())
        {
            result++;
            te_next_time->RemoveAt(i);
            te_func_num->RemoveAt(i);
            te_rate->RemoveAt(i);
            te_identifier->RemoveAt(i);
        }
        else
        {
            i++;
        }
    }

    self->SetTE_NextTime(te_next_time);
    self->SetTE_FuncNum(te_func_num);
    self->SetTE_Rate(te_rate);
    self->SetTE_Identifier(te_identifier);

    te_next_time->Release();
    te_func_num->Release();
    te_rate->Release();
    te_identifier->Release();

    return result;*/
    return 0;
}
