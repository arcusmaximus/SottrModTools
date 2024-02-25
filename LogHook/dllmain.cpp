#include "pch.h"

BOOL DllMain(HMODULE hModule, DWORD  ul_reason_for_call, LPVOID lpReserved)
{
    switch (ul_reason_for_call)
    {
        case DLL_PROCESS_ATTACH:
            SottrHook::Install();
            break;
    }
    return TRUE;
}

