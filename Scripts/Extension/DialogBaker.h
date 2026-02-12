#pragma once

#include "Common.h"

#include "Baker.h"
#include "FileSystem.h"

FO_BEGIN_NAMESPACE

FO_DECLARE_EXCEPTION(DialogBakerException);

class DialogBaker final : public BaseBaker
{
public:
    static constexpr string_view_nt NAME = "Dialog";

    explicit DialogBaker(shared_ptr<BakingContext> ctx);
    DialogBaker(const DialogBaker&) = delete;
    DialogBaker(DialogBaker&&) noexcept = delete;
    auto operator=(const DialogBaker&) = delete;
    auto operator=(DialogBaker&&) noexcept = delete;
    ~DialogBaker() override = default;

    [[nodiscard]] auto GetName() const -> string_view override { return NAME; }
    [[nodiscard]] auto GetOrder() const -> int32 override { return 5; }

    void BakeFiles(const FileCollection& files, string_view target_path) const override;
};

class DialogTextBaker final : public BaseBaker
{
public:
    static constexpr string_view_nt NAME = "DialogText";

    explicit DialogTextBaker(shared_ptr<BakingContext> ctx);
    DialogTextBaker(const DialogTextBaker&) = delete;
    DialogTextBaker(DialogTextBaker&&) noexcept = delete;
    auto operator=(const DialogTextBaker&) = delete;
    auto operator=(DialogTextBaker&&) noexcept = delete;
    ~DialogTextBaker() override = default;

    [[nodiscard]] auto GetName() const -> string_view override { return NAME; }
    [[nodiscard]] auto GetOrder() const -> int32 override { return 5; }

    void BakeFiles(const FileCollection& files, string_view target_path) const override;
};

FO_END_NAMESPACE
