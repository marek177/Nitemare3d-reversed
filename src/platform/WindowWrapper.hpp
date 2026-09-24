#pragma once

#include "platform/NativeHandleWrapper.hpp"

#include <cstdint>

namespace nitemare3d::port {

using WindowHandle = std::uintptr_t;

class WindowWrapper {
public:
    WindowWrapper() = default;
    WindowWrapper(WindowHandle handle, HandleOwnership ownership) noexcept
        : handle_(handle, ownership) {}

    [[nodiscard]] WindowHandle handle() const noexcept { return handle_.get(); }
    [[nodiscard]] HandleOwnership ownership() const noexcept { return handle_.ownership(); }
    [[nodiscard]] bool ownsWindow() const noexcept { return handle_.ownsHandle(); }

    void attach(WindowHandle handle, HandleOwnership ownership) noexcept {
        handle_.attach(handle, ownership);
    }

    [[nodiscard]] WindowHandle detach() noexcept {
        return handle_.detach();
    }

    // Mirrors the recovered temporary CWnd cleanup rule: remove the borrowed
    // association before object destruction so the native window survives.
    void prepareTemporaryCleanup() noexcept {
        handle_.clearBorrowed();
        associatedObject_ = nullptr;
    }

    void setParentContext(WindowHandle handle) noexcept { parentContext_ = handle; }
    [[nodiscard]] WindowHandle parentContext() const noexcept { return parentContext_; }

    void setAssociatedObject(void* object) noexcept { associatedObject_ = object; }
    [[nodiscard]] void* associatedObject() const noexcept { return associatedObject_; }

private:
    NativeHandleWrapper<WindowHandle> handle_;
    WindowHandle parentContext_ = 0;
    void* associatedObject_ = nullptr;
};

} // namespace nitemare3d::port
