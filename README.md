# Changelog Scraper
Scripts for scraping changelogs from your dependencies.

Each step is composed of a different module for maximum flexibility. You are free to use them as you wish.
For example, lets say you are upgrading to django 3 and want to check what package versions you need:
1. `cat requirements.txt | python github_link_getter.py > out.txt`
2. `cat out.txt | changelog_getter.py -t TOKEN -o changelogs`
3. `cd changelogs && grep "django 3" -iR | less`

Once you have the downloaded changelog files you are free to interact with them as you wish.
You might do a simple grep, or get fancy by trying to parse the changelog.

Changelog parsers:
* https://www.npmjs.com/package/changelog-parser
* https://github.com/cyberark/parse-a-changelog