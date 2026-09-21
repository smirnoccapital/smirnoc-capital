# smirnoc-capital

Source for the Smirnoc Capital analysis site, built with Jekyll and hosted on
GitHub Pages at https://smirnoccapital.github.io/smirnoc-capital/.

## How content gets published

Every analysis piece — whether from a daily automated scan of agricultural
policy/trade news, or from material provided manually — goes through a pull
request before it's live:

1. A branch (`analysis/YYYY-MM-DD-slug`) is created with:
   - `_posts/YYYY-MM-DD-slug.md` — the analysis post
   - `_social/YYYY-MM-DD-slug.md` — matching LinkedIn + X/tweet drafts
     (excluded from the built site, version-controlled only)
2. A PR is opened summarizing the piece for review.
3. Once reviewed/edited and merged to `main`, GitHub Pages rebuilds the site
   automatically.

`_meta/covered-topics.md` tracks what's already been written up, so the
daily scan doesn't repeat a story.

## Local preview

```
bundle install
bundle exec jekyll serve
```
