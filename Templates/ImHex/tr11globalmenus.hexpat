/*
  Parses the main DTPs in:
      global_menus.drm
      fontuniversal.drm
      fontbuttonicons.drm
      fontnvidia.drm
      pregame_menus.drm
      loadingscreen.drm
      ingame_menus.drm
      campsite_menus.drm
 And possibly others
*/

#include "tr11common.hexpat"

struct FlashFile
{
    padding[0x10];
    u32 dtpId;
    padding[0x220 - 0x14];
    InternalRef nameRef;
    if (nameRef.targetPos >= 0)
        char name[] @ nameRef.targetPos;
};

struct FlashFileSet
{
    u32 numFiles;
    padding[4];
    InternalRef filesRef;
    if (filesRef.targetPos >= 0)
        FlashFile files[numFiles] @ filesRef.targetPos;
};

struct SetsRef
{
    InternalRef setsRef @ gResourceBodyPos;
    if (setsRef.targetPos >= 0)
        FlashFileSet sets[2] @ setsRef.targetPos + 8;
};

RefDefinitions refDefinitions @ 0;
SetsRef setsRef @ gResourceBodyPos;
