#pragma once

#include "platform/HandleRegistry.hpp"
#include "platform/WindowWrapper.hpp"

namespace nitemare3d::port {

class WindowRegistry {
public:
    void beginTemporaryScope() noexcept { ++temporaryScopeDepth_; }

    void endTemporaryScope() noexcept {
        if (temporaryScopeDepth_ == 0) return;
        --temporaryScopeDepth_;
        if (temporaryScopeDepth_ == 0) clearTemporary();
    }

    [[nodiscard]] std::size_t temporaryScopeDepth() const noexcept { return temporaryScopeDepth_; }

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
    std::size_t temporaryScopeDepth_ = 0;
};


class TemporaryWindowScope {
public:
    explicit TemporaryWindowScope(WindowRegistry& registry) noexcept
        : registry_(&registry) {
        registry_->beginTemporaryScope();
    }

    TemporaryWindowScope(const TemporaryWindowScope&) = delete;
    TemporaryWindowScope& operator=(const TemporaryWindowScope&) = delete;

    TemporaryWindowScope(TemporaryWindowScope&& other) noexcept
        : registry_(other.registry_) {
        other.registry_ = nullptr;
    }

    TemporaryWindowScope& operator=(TemporaryWindowScope&& other) noexcept {
        if (this == &other) return *this;
        release();
        registry_ = other.registry_;
        other.registry_ = nullptr;
        return *this;
    }

    ~TemporaryWindowScope() { release(); }

    void release() noexcept {
        if (registry_ == nullptr) return;
        registry_->endTemporaryScope();
        registry_ = nullptr;
    }

private:
    WindowRegistry* registry_;
};

} // namespace nitemare3d::port
