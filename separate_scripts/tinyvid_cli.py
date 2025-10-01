#!/usr/bin/env python3
"""
TinyVid CLI - Offline video compression using FFmpeg
Replicates tinyvid.io compression without the browser
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

class TinyVidCLI:
    """CLI tool to compress videos like tinyvid.io"""
    
    # Based on discovered command from tinyvid.io
    DEFAULT_MP4_SETTINGS = {
        "video_codec": "libx264",
        "crf": 28,
        "pixel_format": "yuv420p",
        "audio_codec": "aac",
        "audio_bitrate": "128k",
        "movflags": "+faststart"
    }
    
    # Quality presets (CRF values)
    QUALITY_PRESETS = {
        "high": 23,      # Higher quality, larger file
        "medium": 28,    # Default (tinyvid.io default)
        "low": 32,       # Lower quality, smaller file
        "extreme": 35    # Very compressed
    }
    
    def __init__(self):
        self.check_ffmpeg()
    
    def check_ffmpeg(self):
        """Check if FFmpeg is installed"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✓ FFmpeg found")
                return True
        except FileNotFoundError:
            print("✗ FFmpeg not found!")
            print("\nPlease install FFmpeg:")
            print("  - Windows: https://www.gyan.dev/ffmpeg/builds/")
            print("  - Or use: winget install ffmpeg")
            sys.exit(1)
    
    def compress_video(self, input_file, output_file=None, quality="medium", 
                      keep_resolution=True, max_resolution=None, scale_height=None):
        """
        Compress video using TinyVid's method
        
        Args:
            input_file: Path to input video
            output_file: Path to output video (optional)
            quality: Quality preset (high/medium/low/extreme)
            keep_resolution: Keep original resolution
            max_resolution: Max resolution (e.g., "1920:1080")
            scale_height: Shorthand to scale by height (e.g., 480, 720, 1080)
        """
        
        # Validate input
        if not os.path.exists(input_file):
            print(f"✗ Input file not found: {input_file}")
            return False
        
        # Generate output filename
        if not output_file:
            input_path = Path(input_file)
            output_file = str(input_path.parent / f"{input_path.stem}_compressed{input_path.suffix}")
        
        # Get CRF value for quality
        crf = self.QUALITY_PRESETS.get(quality, 28)
        
        # Build FFmpeg command (exactly like tinyvid.io)
        cmd = [
            "ffmpeg",
            "-i", input_file,
            "-c:v", self.DEFAULT_MP4_SETTINGS["video_codec"],
            "-crf", str(crf),
            "-pix_fmt", self.DEFAULT_MP4_SETTINGS["pixel_format"],
            "-c:a", self.DEFAULT_MP4_SETTINGS["audio_codec"],
            "-b:a", self.DEFAULT_MP4_SETTINGS["audio_bitrate"],
            "-movflags", self.DEFAULT_MP4_SETTINGS["movflags"],
        ]
        
        # Add resolution scaling if needed
        scale_filter = None
        if scale_height:
            # Use shorthand: scale to specific height, maintain aspect ratio
            scale_filter = f"-2:{scale_height}"
        elif max_resolution:
            # Use provided resolution string
            scale_filter = max_resolution
        
        if scale_filter:
            cmd.extend(["-vf", f"scale={scale_filter}"])
        
        # Add output file
        cmd.append(output_file)
        
        # Print command
        print("\n" + "="*60)
        print("🎬 Running FFmpeg Command:")
        print("="*60)
        print(" ".join(cmd))
        print("="*60 + "\n")
        
        # Get input file size
        input_size = os.path.getsize(input_file)
        print(f"📦 Input size: {self.format_size(input_size)}")
        
        # Run FFmpeg
        try:
            result = subprocess.run(
                cmd,
                capture_output=False,  # Show FFmpeg output
                text=True
            )
            
            if result.returncode == 0:
                # Get output file size
                output_size = os.path.getsize(output_file)
                reduction = ((input_size - output_size) / input_size) * 100
                
                print("\n" + "="*60)
                print("✅ Compression Complete!")
                print("="*60)
                print(f"📦 Output size: {self.format_size(output_size)}")
                print(f"📊 Size reduction: {reduction:.1f}%")
                print(f"💾 Saved: {self.format_size(input_size - output_size)}")
                print(f"📁 Output file: {output_file}")
                print("="*60)
                
                return True
            else:
                print(f"\n✗ Compression failed with code {result.returncode}")
                return False
                
        except Exception as e:
            print(f"\n✗ Error: {e}")
            return False
    
    @staticmethod
    def format_size(bytes):
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} TB"
    
    def batch_compress(self, input_files, quality="medium", scale_height=None):
        """Compress multiple videos"""
        print(f"\n🔄 Batch processing {len(input_files)} file(s)...")
        
        results = []
        for i, input_file in enumerate(input_files, 1):
            print(f"\n[{i}/{len(input_files)}] Processing: {input_file}")
            success = self.compress_video(input_file, quality=quality, scale_height=scale_height)
            results.append((input_file, success))
        
        # Summary
        print("\n" + "="*60)
        print("📊 Batch Processing Summary")
        print("="*60)
        successful = sum(1 for _, success in results if success)
        print(f"✓ Successful: {successful}/{len(results)}")
        print(f"✗ Failed: {len(results) - successful}/{len(results)}")
        print("="*60)

def main():
    parser = argparse.ArgumentParser(
        description="TinyVid CLI - Compress videos like tinyvid.io (without the browser!)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compress with default (medium) quality
  python tinyvid_cli.py video.mp4
  
  # Compress with high quality
  python tinyvid_cli.py video.mp4 -q high
  
  # Specify output file
  python tinyvid_cli.py video.mp4 -o compressed.mp4
  
  # Batch compress multiple videos
  python tinyvid_cli.py video1.mp4 video2.mp4 video3.mp4
  
  # Scale to 720p (maintains aspect ratio)
  python tinyvid_cli.py 4k_video.mp4 -s 720
  
  # Scale to 480p (maintains aspect ratio)
  python tinyvid_cli.py video.mp4 -s 480
  
  # Scale to any height (e.g., 360p, 540p, 900p, etc.)
  python tinyvid_cli.py video.mp4 -s 360
  
  # Custom resolution string (for advanced users)
  python tinyvid_cli.py 4k_video.mp4 -r "1280:720"
        """
    )
    
    parser.add_argument(
        "input",
        nargs="+",
        help="Input video file(s)"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file (only for single file)"
    )
    
    parser.add_argument(
        "-q", "--quality",
        choices=["high", "medium", "low", "extreme"],
        default="medium",
        help="Compression quality (default: medium, same as tinyvid.io)"
    )
    
    parser.add_argument(
        "-r", "--resolution",
        help="Scale to resolution (e.g., '1920:1080')"
    )
    
    parser.add_argument(
        "-s", "--scale",
        type=int,
        metavar="HEIGHT",
        help="Scale to specific height in pixels (e.g., 480, 720, 1080), maintains aspect ratio"
    )
    
    args = parser.parse_args()
    
    # Create CLI instance
    cli = TinyVidCLI()
    
    # Single or batch processing
    if len(args.input) == 1:
        # Single file
        cli.compress_video(
            args.input[0],
            output_file=args.output,
            quality=args.quality,
            keep_resolution=(args.resolution is None and args.scale is None),
            max_resolution=args.resolution,
            scale_height=args.scale
        )
    else:
        # Batch processing
        if args.output:
            print("⚠ Warning: -o/--output ignored for batch processing")
        cli.batch_compress(args.input, quality=args.quality, scale_height=args.scale)

if __name__ == "__main__":
    main()

