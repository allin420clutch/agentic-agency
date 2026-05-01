#!/bin/bash
echo "🦞 Automation Report: Trending Sticker Sprint"
echo "Date: $(date +'%B %d, %Y')"
echo "Target Marketplace: SDS Supplies (Shopify)"
echo "================================================="
echo "Scanning for trends..."
python3 trend_hunter.py
echo "Generating images based on trends..."
python3 image_generator.py
echo "Removing backgrounds and preparing SVG/PNGs..."
python3 clean_stickers.py
echo "Syncing final assets to Shopify as ACTIVE products..."
python3 sync_shopify_cli.py
echo "================================================="
echo "🦞 Sync complete! Check your LIVE store."
