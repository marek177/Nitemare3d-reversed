#include "re/Win16MfcAddresses.hpp"

#include <cassert>

int main() {
    using namespace nitemare3d::re::win16;

    static_assert(kMfcAddressCatalog.size() == 33);

    const auto* wndCtor = findMfcAddress(MfcAddressKind16::Code, 1, 0x114A);
    assert(wndCtor != nullptr);

    const auto* cdcAttach = findMfcAddress(MfcAddressKind16::Code, 1, 0x02E2);
    const auto* cdcDetach = findMfcAddress(MfcAddressKind16::Code, 1, 0x0316);
    assert(cdcAttach != nullptr && cdcDetach != nullptr);

    const auto* wndClass = findMfcAddress(MfcAddressKind16::RuntimeClass, 10, 0x0594);
    assert(wndClass != nullptr);

    const auto* wndMap = findMfcAddress(MfcAddressKind16::HandleMap, 10, 0x4250);
    assert(wndMap != nullptr);

    const auto* sentinel = findMfcAddress(MfcAddressKind16::StaticObject, 10, 0x420A);
    assert(sentinel != nullptr);

    assert(findMfcAddress(MfcAddressKind16::Code, 10, 0x4250) == nullptr);
    assert(findMfcAddress(MfcAddressKind16::Code, 1, 0xFFFF) == nullptr);
    return 0;
}
