#!/bin/bash
# ------------------------------------------------------------------------------
# Adapted from: https://github.com/community-scripts/ProxmoxVE/pull/14314
#
# Download NLTK data packages directly from GitHub, bypassing Python.
# Avoids CPU-instruction failures (SIGILL) on older hardware lacking AVX.
#
# Intended for use during Docker image build only.
#
# Environment:
#   NLTK_DATA - Target directory for NLTK data (default: /usr/share/nltk_data)
#
# Returns: 0 on success, non-zero if any package failed
# ------------------------------------------------------------------------------
set -euo pipefail

NLTK_INDEX_URL="https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/index.xml"
PACKAGES="averaged_perceptron_tagger_eng"
TARGET_DIR="${NLTK_DATA:-/usr/share/nltk_data}"

echo "Fetching NLTK package index..."
index_xml=$(curl -fsSL "$NLTK_INDEX_URL")

mkdir -p "$TARGET_DIR"

for pkg in $PACKAGES; do
  echo "Installing NLTK package: $pkg"

  pkg_line=$(echo "$index_xml" | grep "id=\"${pkg}\"" | head -1)
  if [[ -z "$pkg_line" ]]; then
    echo "ERROR: NLTK package not found in index: $pkg" >&2
    exit 1
  fi

  subdir=$(echo "$pkg_line" | grep -oP 'subdir="\K[^"]+')
  pkg_url=$(echo "$pkg_line" | grep -oP 'url="\K[^"]+')
  do_unzip=$(echo "$pkg_line" | grep -oP 'unzip="\K[^"]+')

  if [[ -z "$subdir" || -z "$pkg_url" ]]; then
    echo "ERROR: Could not parse NLTK index entry for: $pkg" >&2
    exit 1
  fi

  mkdir -p "${TARGET_DIR}/${subdir}"
  tmp_zip=$(mktemp --suffix=.zip)

  echo "Downloading: $pkg_url"
  curl -fsSL -o "$tmp_zip" "$pkg_url"

  if [[ "$do_unzip" == "1" ]]; then
    unzip -q -o "$tmp_zip" -d "${TARGET_DIR}/${subdir}/"
    rm -f "$tmp_zip"
  else
    mv "$tmp_zip" "${TARGET_DIR}/${subdir}/${pkg}.zip"
  fi

  echo "Done: $pkg"
done
