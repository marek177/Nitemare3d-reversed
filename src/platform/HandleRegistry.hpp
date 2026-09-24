#pragma once

#include <cstdint>
#include <optional>
#include <unordered_map>

namespace nitemare3d::port {

// Modern behavioral model for the recovered Win16 HandleMap semantics.
// This deliberately does not emulate MFC 2.5 binary layouts or 16:16 pointers.
template <class Handle, class Wrapper>
class HandleRegistry {
public:
    Wrapper* findPermanent(Handle handle) noexcept {
        const auto it = permanent_.find(handle);
        return it == permanent_.end() ? nullptr : &it->second;
    }

    Wrapper* findTemporary(Handle handle) noexcept {
        const auto it = temporary_.find(handle);
        return it == temporary_.end() ? nullptr : &it->second;
    }

    template <class Factory>
    Wrapper& fromHandle(Handle handle, Factory&& factory) {
        if (auto* wrapper = findPermanent(handle)) return *wrapper;
        if (auto* wrapper = findTemporary(handle)) return *wrapper;
        auto [it, inserted] = temporary_.emplace(handle, factory(handle));
        (void)inserted;
        return it->second;
    }

    void attachPermanent(Handle handle, Wrapper wrapper) {
        temporary_.erase(handle);
        permanent_.insert_or_assign(handle, std::move(wrapper));
    }

    std::optional<Wrapper> detachPermanent(Handle handle) {
        const auto it = permanent_.find(handle);
        if (it == permanent_.end()) return std::nullopt;
        Wrapper wrapper = std::move(it->second);
        permanent_.erase(it);
        return wrapper;
    }

    void clearTemporary() noexcept {
        temporary_.clear();
    }

    [[nodiscard]] std::size_t permanentCount() const noexcept { return permanent_.size(); }
    [[nodiscard]] std::size_t temporaryCount() const noexcept { return temporary_.size(); }

private:
    std::unordered_map<Handle, Wrapper> permanent_;
    std::unordered_map<Handle, Wrapper> temporary_;
};

enum class ZOrderTarget {
    Top,
    Bottom,
    TopMost,
    NoTopMost,
};

} // namespace nitemare3d::port
