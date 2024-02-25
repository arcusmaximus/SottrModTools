using SottrModManager.Shared.Cdc;
using SottrModManager.Shared.Util;
using System;
using System.IO;
using System.IO.MemoryMappedFiles;
using System.Threading;

namespace SottrExtractor.LogHook
{
    internal class NotificationChannel : IDisposable
    {
        private readonly EventWaitHandle _availableEvent;
        private readonly EventWaitHandle _receivedEvent;
        private readonly MemoryMappedFile _buffer;
        private readonly Stream _stream;
        private readonly BinaryReader _reader;

        public NotificationChannel()
        {
            _availableEvent = new EventWaitHandle(false, EventResetMode.AutoReset, "SottrLogHook_NotificationAvailableEvent");
            _receivedEvent = new EventWaitHandle(false, EventResetMode.AutoReset, "SottrLogHook_NotificationReceivedEvent");
            _buffer = MemoryMappedFile.CreateNew("SottrLogHook_NotificationBuffer", 0x1000);
            _stream = _buffer.CreateViewStream();
            _reader = new BinaryReader(_stream);
        }

        public void Listen(CancellationToken cancellationToken)
        {
            while (!cancellationToken.IsCancellationRequested)
            {
                try
                {
                    if (!_availableEvent.WaitOne(5000))
                        continue;
                }
                catch
                {
                    break;
                }

                _stream.Position = 0;
                EventType type = (EventType)_reader.ReadByte();
                switch (type)
                {
                    case EventType.OpeningFile:
                        RaiseOpeningFile();
                        break;

                    case EventType.PlayingAnimation:
                        RaisePlayingAnimation();
                        break;

                    default:
                        _receivedEvent.Set();
                        break;
                }
            }
        }

        private void RaiseOpeningFile()
        {
            ulong nameHash = _reader.ReadUInt64();
            ulong locale = _reader.ReadUInt64();
            string path = _reader.ReadZeroTerminatedString();
            _receivedEvent.Set();
            OpeningFile?.Invoke(new ArchiveFileKey(nameHash, locale), path);
        }

        private void RaisePlayingAnimation()
        {
            int id = _reader.ReadInt32();
            string name = _reader.ReadZeroTerminatedString();
            _receivedEvent.Set();
            PlayingAnimation?.Invoke(id, name);
        }

        public delegate void OpeningFileHandler(ArchiveFileKey key, string path);
        public event OpeningFileHandler OpeningFile;

        public delegate void PlayingAnimationHandler(int id, string name);
        public event PlayingAnimationHandler PlayingAnimation;

        private enum EventType
        {
            OpeningFile,
            PlayingAnimation
        }

        public void Dispose()
        {
            _availableEvent.Dispose();
            _receivedEvent.Dispose();
            _buffer.Dispose();
        }
    }
}
