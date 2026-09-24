#pragma once

#include "platform/HandleRegistry.hpp"
#include "platform/WindowWrapper.hpp"

namespace nitemare3d::port {

class WindowRegistry {
public:
    WindowWrapper& fromHandle(WindowHandle handle) {
        return registry_.fromHandle(handle, [](WindowHandle value) {
            return WindowWrapper{value, HandleOwnership::Borrowed};
        });
    }

    void attachOwned(WindowHandle handle) {
        registry_.attachPermanent(handle, WindowWrapper{handle, HandleOwnership::Owned});
    }

    void attachBorrowedPermanent(WindowHandle handle) {
        registry_.attachPermanent(handle, WindowWrapper{handle, HandleOwnership::Borrowed});
    }

    [[nodiscard]] WindowWrapper* findPermanent(WindowHandle handle) noexcept {
        return registry_.findPermanent(handle);
    }

    [[nodiscard]] WindowWrapper* findTemporary(WindowHandle handle) noexcept {
        return registry_.findTemporary(handle);
    }

    [[nodiscard]] WindowHandle detach(WindowHandle handle) {
        auto wrapper = registry_.detachPermanent(handle);
        return wrapper ? wrapper->detach() : WindowHandle{};
    }

    void clearTemporary() noexcept {
        registry_.clearTemporary();
    }

    [[nodiscard]] std::size_t permanentCount() const noexcept {
        return registry_.permanentCount();
    }

    [[nodiscard]] std::size_t temporaryCount() const noexcept {
        return registry_.temporaryCount();
    }

private:
    HandleRegistry<WindowHandle, WindowWrapper> registry_;
};

} // namespace nitemare3d::port
