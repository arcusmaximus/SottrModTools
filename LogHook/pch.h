#pragma once

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <format>

typedef uint64_t QWORD;

#include "../vendor/Detours/src/detours.h"

#include "Sottr/AnimLibItem.h"
#include "Sottr/TigerArchiveFileEntry.h"

#include "NotificationChannel.h"
#include "SottrHook.h"
