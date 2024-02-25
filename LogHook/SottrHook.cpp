#include "pch.h"

extern "C"
{
    void* SottrAddr_RequestFile;
    void* SottrAddr_GetAnimation;

    void SottrHook_RequestFile();
    void SottrHook_GetAnimation();

    void SottrHandler_RequestFile(const Sottr::TigerArchiveFileEntry* pEntry, const char* pszPath)
    {
        NotificationChannel::Instance.NotifyOpeningFile(pEntry->nameHash, pEntry->locale, pszPath);
    }

    void SottrHandler_GetAnimation(Sottr::AnimLibItem* pAnim)
    {
        NotificationChannel::Instance.NotifyPlayingAnimation(pAnim->id, pAnim->pszName);
    }
}

void SottrHook::Install()
{
    BYTE* pGame = (BYTE*)GetModuleHandle(nullptr);
    SottrAddr_RequestFile = pGame + 0x1C8018;
    SottrAddr_GetAnimation = pGame + 0x12BCA2;

    DetourTransactionBegin();
    DetourAttach(&SottrAddr_RequestFile, SottrHook_RequestFile);
    DetourAttach(&SottrAddr_GetAnimation, SottrHook_GetAnimation);
    DetourTransactionCommit();
}
