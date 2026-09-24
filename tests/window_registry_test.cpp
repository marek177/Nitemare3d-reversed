#include "platform/WindowRegistry.hpp"

#include <cassert>

int main() {
    using namespace nitemare3d::port;

    WindowRegistry windows;

    auto& first = windows.fromHandle(100);
    auto* firstAddress = &first;
    assert(first.handle() == 100);
    assert(!first.ownsWindow());
    assert(windows.temporaryCount() == 1);

    auto& second = windows.fromHandle(100);
    assert(&second == firstAddress);

    windows.attachOwned(200);
    auto& owned = windows.fromHandle(200);
    assert(owned.ownsWindow());
    assert(windows.permanentCount() == 1);

    windows.attachBorrowedPermanent(300);
    assert(!windows.fromHandle(300).ownsWindow());
    assert(windows.permanentCount() == 2);

    assert(windows.detach(200) == 200);
    assert(windows.permanentCount() == 1);

    windows.clearTemporary();
    assert(windows.temporaryCount() == 0);
    return 0;
}
