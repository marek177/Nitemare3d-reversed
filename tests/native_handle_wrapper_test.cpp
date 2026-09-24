#include "platform/NativeHandleWrapper.hpp"

#include <cassert>

int main() {
    using namespace nitemare3d::port;

    NativeHandleWrapper<int> borrowed{42, HandleOwnership::Borrowed};
    assert(borrowed.valid());
    assert(!borrowed.ownsHandle());
    borrowed.clearBorrowed();
    assert(!borrowed.valid());

    NativeHandleWrapper<int> owned{77, HandleOwnership::Owned};
    owned.clearBorrowed();
    assert(owned.get() == 77);
    assert(owned.ownsHandle());
    assert(owned.detach() == 77);
    assert(!owned.valid());
    assert(!owned.ownsHandle());

    NativeHandleWrapper<int> sentinel{-1, HandleOwnership::Sentinel};
    assert(sentinel.valid());
    assert(!sentinel.ownsHandle());
    sentinel.clearBorrowed();
    assert(!sentinel.valid());

    return 0;
}
