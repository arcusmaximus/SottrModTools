using System;
using System.IO;

namespace SottrModManager.Shared.Util
{
    public class WindowedStream : Stream
    {
        private readonly Stream _inner;
        private readonly long _startPos;
        private readonly long _length;

        public WindowedStream(Stream inner, long startPos, long length)
        {
            if (!inner.CanSeek)
                throw new ArgumentException("Inner stream must support seeking");

            _inner = inner;
            _startPos = startPos;
            _length = length;

            _inner.Position = startPos;
        }

        public override bool CanRead => _inner.CanRead;

        public override bool CanSeek => true;

        public override bool CanWrite => _inner.CanWrite;

        public override long Position
        {
            get { return _inner.Position - _startPos; }
            set
            {
                if (value < 0 || value > _length)
                    throw new ArgumentOutOfRangeException();

                _inner.Position = _startPos + value;
            }
        }

        public override long Length => _length;

        public override long Seek(long offset, SeekOrigin origin)
        {
            long newPos = origin switch
            {
                SeekOrigin.Begin => offset,
                SeekOrigin.Current => Position + offset,
                SeekOrigin.End => Position + Length + offset
            };
            newPos = Math.Min(Math.Max(newPos, 0), Length);
            Position = newPos;
            return newPos;
        }

        public override int Read(byte[] buffer, int offset, int count)
        {
            count = Math.Min(count, (int)Math.Min(Length - Position, int.MaxValue));
            return _inner.Read(buffer, offset, count);
        }

        public override int Read(Span<byte> buffer)
        {
            int count = Math.Min(buffer.Length, (int)Math.Min(Length - Position, int.MaxValue));
            if (count < buffer.Length)
                buffer = buffer[..count];

            return _inner.Read(buffer);
        }

        public override void SetLength(long value)
        {
            throw new NotSupportedException();
        }

        public override void Write(byte[] buffer, int offset, int count)
        {
            if (count > Length - Position)
                throw new ArgumentOutOfRangeException();

            _inner.Write(buffer, offset, count);
        }

        public override void Write(ReadOnlySpan<byte> buffer)
        {
            if (buffer.Length > Length - Position)
                throw new ArgumentOutOfRangeException();

            _inner.Write(buffer);
        }

        public override void Flush()
        {
            _inner.Flush();
        }
    }
}
