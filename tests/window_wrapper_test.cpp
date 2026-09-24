#include "platform/WindowWrapper.hpp"

#include <cassert>

int main() {
    using namespace nitemare3d::port;

    WindowWrapper temporary{100, HandleOwnership::Borrowed};
    temporary.setParentContext(50);
    int associated = 7;
    temporary.setAssociatedObject(&associated);

    assert(temporary.handle() == 100);
    assert(temporary.parentContext() == 50);
    assert(temporary.associatedObject() == &associated);
    assert(!temporary.ownsWindow());

    temporary.prepareTemporaryCleanup();
    assert(temporary.handle() == 0);
    assert(temporary.associatedObject() == nullptr);

    WindowWrapper owned{200, HandleOwnership::Owned};
    owned.prepareTemporaryCleanup();
    assert(owned.handle() == 200);
    assert(owned.ownsWindow());
    assert(owned.detach() == 200);
    assert(owned.handle() == 0);

    return 0;
}
