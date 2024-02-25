#pragma once

namespace Sottr
{
    struct TigerArchiveFileEntry
    {
        QWORD nameHash;
        QWORD locale;
        int uncompressedSize;
        int compressedSize;
        short archivePart;
        short archiveId;
        int offset;
    };
}
