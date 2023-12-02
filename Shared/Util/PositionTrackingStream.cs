using System;
using System.IO;

namespace SottrModManager.Shared.Util
{
    public class PositionTrackingStream : Stream
    {
        private readonly Stream _inner;
        private long _position;

        public PositionTrackingStream(Stream inner)
        {
            _inner = inner;
        }

        public override void Flush()
        {
            _inner.Flush();
        }

        public override long Seek(long offset, SeekOrigin origin)
        {
            throw new NotSupportedException();
        }

        public override void SetLength(long value)
        {
            _inner.SetLength(value);
        }

        public override int Read(byte[] buffer, int offset, int count)
        {
            int amountRead = _inner.Read(buffer, offset, count);
            _position += amountRead;
            return amountRead;
        }

        public override void Write(byte[] buffer, int offset, int count)
        {
            _inner.Write(buffer, offset, count);
            _position += count;
        }

        public override bool CanRead => _inner.CanRead;

        public override bool CanSeek => false;

        public override bool CanWrite => _inner.CanWrite;

        public override long Length => _inner.Length;

        public override long Position
        {
            get => _position;
            set => throw new NotSupportedException();
        }

        protected override void Dispose(bool disposing)
        {
            base.Dispose(disposing);
            _inner.Dispose();
        }
    }
}
