#!/bin/bash
# Run MfaText without installation

cd "$(dirname "$0")"
python3 -m mfatext.main "$@"

