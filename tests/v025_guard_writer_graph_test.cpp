#include "re/N3DV025GuardWriterGraph.hpp"

#include <cassert>

int main() {
    using namespace n3d::re::v025;

    static_assert(kWin16WriterGraph.size() == 17);
    static_assert(countWritersFor(GuardField::State) >= 9);
    static_assert(countWritersFor(GuardField::NextState) == 2);

    constexpr auto* s01 = writer("state01_to_02");
    static_assert(s01 != nullptr);
    static_assert(s01->addressKnown);
    static_assert(s01->segment == 0x0003);
    static_assert(s01->offset == 0x7BE0);
    static_assert(s01->value == 0x02);

    constexpr auto* pain = writer("normal_pain_enter_15");
    static_assert(pain != nullptr);
    static_assert(!pain->addressKnown);
    static_assert(pain->value == 0x15);
    static_assert(pain->confidence == Confidence::Confirmed);

    constexpr auto* dracula = writer("dracula_transform_nextstate");
    static_assert(dracula != nullptr);
    static_assert(!dracula->addressKnown);
    static_assert(dracula->value == 0x02);
    static_assert(dracula->confidence == Confidence::Confirmed);

    static_assert(hasKnownAddress("state15_return"));
    static_assert(!hasKnownAddress("normal_pain_enter_15"));
    static_assert(isConfirmedWriter("state15_return"));
    static_assert(isPainEntryInvariant());

    assert(writer("not_a_real_writer") == nullptr);
    return 0;
}
