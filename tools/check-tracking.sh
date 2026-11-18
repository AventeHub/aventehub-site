#!/usr/bin/env bash
# Release guard (Nov 18, Saam · lesson L-20261114-TRACKINGDROP): every public page must load the tracking script.
# Run: bash tools/check-tracking.sh   (also runs on every push/PR in .github/workflows/tracking-guard.yml)
# Internal tools without tracking go in SKIP.
SKIP='^(\./)?(wa-upload|tools|email|social)/'
fail=0
while IFS= read -r f; do
  [[ "$f" =~ $SKIP ]] && continue
  grep -q '/assets/av-consent.js' "$f" || { echo "❌ no tracking script: $f"; fail=1; }
done < <(find . -name index.html -not -path './.git/*' -not -path './node_modules/*' | sed 's#^\./##' | sort)
for f in index.html builders/catalogue/index.html showroom/index.html; do
  grep -q '/assets/av-visit.js' "$f" || { echo "❌ no visit log (?from=) script: $f"; fail=1; }
done
[ $fail = 0 ] && echo "✅ tracking present on all public pages"
exit $fail
