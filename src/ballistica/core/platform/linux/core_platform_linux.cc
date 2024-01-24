// Released under the MIT License. See LICENSE for details.

#if BA_OSTYPE_LINUX
#include "ballistica/core/platform/linux/core_platform_linux.h"

#include <sys/utsname.h>

#include <cstdlib>
#include <cstring>
#include <string>

namespace ballistica::core {

CorePlatformLinux::CorePlatformLinux() {}

std::string CorePlatformLinux::GenerateUUID() {
  std::string val;
  char buffer[100];
  FILE* fd_out = popen("cat /proc/sys/kernel/random/uuid", "r");
  if (fd_out) {
    int size = fread(buffer, 1, 99, fd_out);
    fclose(fd_out);
    if (size == 37) {
      buffer[size - 1] = 0;  // chop off trailing newline
      val = buffer;
    }
  }
  if (val == "") {
    throw Exception("kernel uuid not available");
  }
  return val;
}

auto CorePlatformLinux::DoGetDeviceDescription() -> std::string {
  // Let's look for something pretty like "Ubuntu 20.04", etc.
  FILE* file = fopen("/etc/os-release", "r");
  std::optional<std::string> out;
  if (file != NULL) {
    char line[256];  // Adjust the buffer size as needed

    while (fgets(line, sizeof(line), file)) {
      if (strstr(line, "PRETTY_NAME=") != nullptr) {
        // Extract the distribution name and version
        char* start = strchr(line, '"');
        char* end = strrchr(line, '"');
        if (start != nullptr && end != nullptr) {
          *end = '\0';  // Remove the trailing quote
          out = start + 1;
        }
        break;
      }
    }
    fclose(file);
  }
  if (out.has_value()) {
    return *out;
  }
  return CorePlatform::GetDeviceDescription();
}

auto CorePlatformLinux::GetOSVersionString() -> std::string {
  std::optional<std::string> out;
  struct utsname uts;
  if (uname(&uts) == 0) {
    out = uts.release;

    // Try to parse 3 version numbers.
    unsigned int major, minor, bugfix;
    if (sscanf(uts.release, "%u.%u.%u", &major, &minor, &bugfix) == 3) {
      char buf[128];
      snprintf(buf, sizeof(buf), "%.u.%u.%u", major, minor, bugfix);
      out = buf;
    }
  }
  if (out.has_value()) {
    return *out;
  }
  return CorePlatform::GetOSVersionString();
}

auto CorePlatformLinux::GetDeviceUUIDInputs() -> std::list<std::string> {
  std::list<std::string> out;

  // For now let's just go with machine-id.
  // Perhaps can add kernel version or something later.
  char buffer[100];
  if (FILE* infile = fopen("/etc/machine-id", "r")) {
    int size = fread(buffer, 1, 99, infile);
    fclose(infile);
    if (size < 10) {
      throw Exception("unexpected machine-id value");
    }
    buffer[size] = 0;
    out.push_back(buffer);
  } else {
    throw Exception("/etc/machine-id not accessible");
  }
  return out;
};

bool CorePlatformLinux::DoHasTouchScreen() { return false; }

std::string CorePlatformLinux::GetPlatformName() { return "linux"; }

std::string CorePlatformLinux::GetSubplatformName() {
#if BA_TEST_BUILD
  return "test";
#else
  return "";
#endif
}

}  // namespace ballistica::core

#endif  // BA_OSTYPE_LINUX
