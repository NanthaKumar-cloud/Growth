import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pipeline import ContentEnginePipeline

def main():
    parser = argparse.ArgumentParser(
        description="IncuBrix Growth Engine - AI Content Generation & Repurposing Pipeline"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/inputs/sample_longform_case_study.md",
        help="Path to long-form source input file"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of platform-specific assets to generate (default: 10)"
    )
    parser.add_argument(
        "--no-render",
        action="store_true",
        help="Skip rendering MP4 videos and PNG carousel slides (faster dry-run)"
    )

    args = parser.parse_args()

    print("=" * 70)
    print(" INCUBRIX GROWTH ENGINE — MULTI-PLATFORM CONTENT PIPELINE")
    print("=" * 70)
    print(f" Input File:   {args.input}")
    print(f" Target Count: {args.count} assets")
    print(f" Media Render: {'Disabled' if args.no_render else 'Enabled (FFmpeg & Pillow)'}")
    print("-" * 70)

    pipeline = ContentEnginePipeline()
    try:
        results = pipeline.run(
            input_source=args.input,
            asset_count=args.count,
            render_media=not args.no_render
        )

        print("\nPIPELINE EXECUTION COMPLETE:")
        print(f"  • Source Document:     {results['source_title']}")
        print(f"  • Assets Generated:    {results['assets_generated']} / {results['assets_requested']}")
        print(f"  • Rejections/Filtered: {results['assets_rejected']}")
        print(f"  • Elapsed Runtime:     {results['telemetry']['elapsed_seconds']} seconds")
        print(f"  • Token Telemetry:     {results['telemetry']['total_tokens']} total tokens")
        print(f"  • Estimated API Cost:  {results['telemetry']['estimated_cost_usd']}")
        print(f"  • Exported Calendar:   {results['calendar_csv_path']}")
        print(f"  • Exported Manifest:   {results['manifest_json_path']}")
        print("=" * 70)

    except Exception as e:
        print(f"\n[PIPELINE ERROR] {type(e).__name__}: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
