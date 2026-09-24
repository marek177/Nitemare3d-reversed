#pragma once

#include <utility>

namespace nitemare3d::port {

enum class HandleOwnership {
    Borrowed,
    Owned,
    Sentinel,
};

template <class Handle>
class NativeHandleWrapper {
public:
    NativeHandleWrapper() = default;
    NativeHandleWrapper(Handle handle, HandleOwnership ownership) noexcept
        : handle_(handle), ownership_(ownership) {}

    [[nodiscard]] Handle get() const noexcept { return handle_; }
    [[nodiscard]] HandleOwnership ownership() const noexcept { return ownership_; }
    [[nodiscard]] bool valid() const noexcept { return handle_ != Handle{}; }
    [[nodiscard]] bool ownsHandle() const noexcept { return ownership_ == HandleOwnership::Owned; }

    void attach(Handle handle, HandleOwnership ownership) noexcept {
        handle_ = handle;
        ownership_ = ownership;
    }

    [[nodiscard]] Handle detach() noexcept {
        Handle old = handle_;
        handle_ = Handle{};
        ownership_ = HandleOwnership::Borrowed;
        return old;
    }

    void clearBorrowed() noexcept {
        if (!ownsHandle()) handle_ = Handle{};
    }

private:
    Handle handle_{};
    HandleOwnership ownership_ = HandleOwnership::Borrowed;
};

} // namespace nitemare3d::port
