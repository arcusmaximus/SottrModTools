#pragma once

class NotificationChannel
{
public:
    NotificationChannel();
    ~NotificationChannel();

    void NotifyOpeningFile(QWORD nameHash, QWORD locale, const char* pszPath);
    void NotifyPlayingAnimation(int id, const char* pszName);

    static NotificationChannel Instance;

private:
    enum class EventType
    {
        OPENING_FILE,
        PLAYING_ANIMATION
    };

    void BeginNotification(EventType type);
    void Write(int value);
    void Write(QWORD value);
    void Write(const char* pszText);
    void EndNotification();

    void Close();

    int RemainingBufferSpace() const;

    HANDLE _hAvailableEvent;
    HANDLE _hReceivedEvent;
    
    HANDLE _hMutex = nullptr;
    HANDLE _hBuffer = nullptr;
    BYTE* _pBuffer = nullptr;
    BYTE* _pWritePos = nullptr;

    const int BufferSize = 0x1000;
};
