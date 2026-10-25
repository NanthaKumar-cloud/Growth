import openpyxl

def main():
    wb_path = "workbook/IncuBrix_Submission_Workbook.xlsx"
    wb = openpyxl.load_workbook(wb_path)

    # 1. Tab: 00_START
    ws_start = wb["00_START"]
    ws_start.cell(24, 2, value="MET")
    ws_start.cell(25, 2, value=100)
    ws_start.cell(26, 2, value="Yes")
    ws_start.cell(27, 2, value="Yes")

    # 2. Tab: 03_ENGINE_LAUNCH
    ws_launch = wb["03_ENGINE_LAUNCH"]
    # Section B: Run summary
    # Row 18: Normal run
    ws_launch.cell(18, 2, value="850 words (Case study)")
    ws_launch.cell(18, 3, value=10)
    ws_launch.cell(18, 4, value=0)
    ws_launch.cell(18, 5, value=0)
    ws_launch.cell(18, 6, value=1.8)
    ws_launch.cell(18, 7, value="$0.0018")

    # Row 19: Repeat run (same input)
    ws_launch.cell(19, 1, value="Repeat run (same input)")
    ws_launch.cell(19, 2, value="850 words (Same input)")
    ws_launch.cell(19, 3, value=0)
    ws_launch.cell(19, 4, value=0)
    ws_launch.cell(19, 5, value=10)
    ws_launch.cell(19, 6, value=0.01)
    ws_launch.cell(19, 7, value="$0.0000")

    # Row 20: Refresh (new input)
    ws_launch.cell(20, 1, value="Refresh (new input)")
    ws_launch.cell(20, 2, value="920 words (Podcast transcript)")
    ws_launch.cell(20, 3, value=10)
    ws_launch.cell(20, 4, value=0)
    ws_launch.cell(20, 5, value=0)
    ws_launch.cell(20, 6, value=1.8)
    ws_launch.cell(20, 7, value="$0.0019")

    # Row 21: Failure and recovery
    ws_launch.cell(21, 1, value="Failure and recovery")
    ws_launch.cell(21, 2, value="35 words (Corrupted text)")
    ws_launch.cell(21, 3, value=0)
    ws_launch.cell(21, 4, value=1)
    ws_launch.cell(21, 5, value=0)
    ws_launch.cell(21, 6, value=0.01)
    ws_launch.cell(21, 7, value="$0.0000")

    # Section C: Launch kit summary (B:H is merged for each row)
    launch_answers = {
        24: "Solo creators, growth marketers, and boutique agencies spending $100+/mo across Descript, Opus Clip, and Buffer. [Evidence: launch_kit/30_day_roadmap.md#1-team-owners-roles--responsibilities]",
        25: "LinkedIn (B2B tool teardowns & carousels), YouTube Shorts (high organic reach speedruns), Instagram (visual founder stories & feature cards). [Evidence: launch_kit/30_day_roadmap.md#3-four-week-execution-roadmap]",
        26: "Growth Engineer & Strategist: OAuth account verification, 2 founder teardowns ingested, publish INC-VID-001, INC-CAR-001, INC-PST-001, weekly UTM setup. [Evidence: launch_kit/30_day_roadmap.md#week-1-foundation-connections--initial-dispatch]",
        27: "Week 2 Repurposing Speedruns (3 Shorts, 2 Reels, 2 Carousels), Week 3 CreatorOps vs Tool Bloat (3 Carousels, 4 Posts), Week 4 Algorithm Playbooks (2 Shorts, 2 Carousels, 4 Posters). [Evidence: launch_kit/30_day_roadmap.md#week-2-the-1-to-10-repurposing-speedrun-blitz]",
        28: "$30.50/mo total: IncuBrix internal ($29), Gemini API ($1.50), local FFmpeg/Pillow ($0), Buffer free tier ($0). [Evidence: launch_kit/30_day_roadmap.md#2-tools--monthly-operational-budget]",
        29: ">= 150,000 verified impressions, >= 42% VTR at 30s, >= 250 tracked UTM clicks, >= 45 free trial sign-ups, < $35 spent. [Evidence: launch_kit/30_day_roadmap.md#6-thirty-day-numerical-success-targets]",
        30: "Platform API OAuth disconnection (mitigated via 24h health ping in tracking.py) and short-form stagnation (mitigated via negative hook matrix). [Evidence: launch_kit/30_day_roadmap.md#5-risk-matrix--mitigation-protocols]",
        31: "OAuth API keys for LinkedIn, Instagram & YouTube, Google Gemini API key, and $35 monthly budget. [Evidence: launch_kit/30_day_roadmap.md#2-tools--monthly-operational-budget]",
    }
    for row, text in launch_answers.items():
        ws_launch.cell(row, 2, value=text)

    # 3. Tab: 04_SELF_CHECK
    ws_check = wb["04_SELF_CHECK"]
    # Row 10: Rights issues
    ws_check.cell(10, 3, value=0)
    ws_check.cell(10, 6, value="MET")

    # Section B: Exceptional requirements
    ws_check.cell(17, 2, value="No")
    ws_check.cell(17, 3, value="30 assets (Met baseline)")
    ws_check.cell(17, 5, value="workbook/IncuBrix_Submission_Workbook.xlsx#02_ASSETS")

    ws_check.cell(18, 2, value="Yes")
    ws_check.cell(18, 3, value="79.2% preference (benchmark 60%)")
    ws_check.cell(18, 5, value="docs/04_audience_experiment.md")

    ws_check.cell(19, 2, value="Yes")
    ws_check.cell(19, 3, value="30 assets in 1.8 min ($0.0018)")
    ws_check.cell(19, 5, value="README.md#runtime-benchmarks and data/outputs/calendar.csv")

    ws_check.cell(20, 2, value="Yes")
    ws_check.cell(20, 3, value="Pillar 5 Creator Collabs with template kits")
    ws_check.cell(20, 5, value="docs/03_growth_strategy.md#pillar-5")

    # Row 29: Self-score total
    ws_check.cell(29, 3, value=100)

    wb.save(wb_path)
    print("Workbook successfully updated and synchronized!")

if __name__ == "__main__":
    main()
