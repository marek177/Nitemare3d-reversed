#include "platform/HandleRegistry.hpp"

#include <cassert>

namespace {
struct Wrapper {
    int handle = 0;
    bool borrowed = true;
};
}

int main() {
    using nitemare3d::port::HandleRegistry;

    HandleRegistry<int, Wrapper> registry;
    int factoryCalls = 0;
    auto factory = [&](int handle) {
        ++factoryCalls;
        return Wrapper{handle, true};
    };

    auto& first = registry.fromHandle(100, factory);
    auto* firstAddress = &first;
    assert(first.borrowed);
    assert(factoryCalls == 1);
    assert(registry.temporaryCount() == 1);

    auto& second = registry.fromHandle(100, factory);
    assert(&second == firstAddress);
    assert(factoryCalls == 1);

    registry.attachPermanent(200, Wrapper{200, false});
    assert(registry.permanentCount() == 1);
    auto& permanent = registry.fromHandle(200, factory);
    assert(!permanent.borrowed);
    assert(factoryCalls == 1);

    auto detached = registry.detachPermanent(200);
    assert(detached.has_value());
    assert(registry.permanentCount() == 0);

    registry.clearTemporary();
    assert(registry.temporaryCount() == 0);
    return 0;
}
