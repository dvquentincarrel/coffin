#!/bin/bash
# Setup script, handles symlink creation

lbin=${1:-"$HOME/.local/bin"}
mkdir -p "$lbin"
ln -si "$PWD/coffin" "$lbin/coffin"
