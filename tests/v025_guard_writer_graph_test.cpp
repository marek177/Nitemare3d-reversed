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
    static_assert(pain->addressKnown);
    static_assert(pain->segment == 3 && pain->offset == 0x8297);
    static_assert(pain->value == 0x15);
    static_assert(pain->confidence == Confidence::Confirmed);

    constexpr auto* dracula = writer("dracula_transform_nextstate");
    static_assert(dracula != nullptr);
    static_assert(dracula->addressKnown);
    static_assert(dracula->segment == 3 && dracula->offset == 0xA17F);
    static_assert(dracula->value == 0x02);
    static_assert(dracula->confidence == Confidence::Confirmed);

    static_assert(hasKnownAddress("state15_return"));
    static_assert(hasKnownAddress("normal_pain_enter_15"));
    static_assert(writer("normal_pain_save_previous_state")->offset == 0x8290);
    static_assert(writer("normal_pain_resoct_8")->offset == 0x81F3);
    static_assert(writer("dracula_transform_class")->offset == 0xA16D);
    static_assert(writer("dracula_transform_state")->offset == 0xA17A);
    static_assert(writer("dracula_transform_timer")->offset == 0xA184);
    static_assert(isConfirmedWriter("state15_return"));
    static_assert(isPainEntryInvariant());

    assert(writer("not_a_real_writer") == nullptr);
    return 0;
}
