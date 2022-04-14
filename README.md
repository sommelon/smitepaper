# Smitepaper
### Smite wallpaper scraper

### Run
```
python3 smitepaper.py
```

### Process
- Grab all the slugs of posts with the tag `Update Notes` on the [https://www.smitegame.com/news/](https://www.smitegame.com/news/) page.
- The slugs are saved to `slugs.txt` and the second time the script is run and the file exists, the slugs are read from there.
- Iterate through each slug, visit every post and write the skin name, link to the image, the image size and the slug to `wallpapers.csv` if it's not there already.
- Note that some skins don't have links to the wallpapers, but they are still written to the csv file.
- The files are kept in this repo, so there is no need to repeat the process, unless they are out of date.
- `gods.txt` contains the names of the gods. Those are not scraped so it needs manual updates.
- To keep the csv file up to date, only keep the slugs from which to grab the new wallpapers. There shouldn't be any duplicates if you run the script twice in a row, but it will be significantly faster.

### TODOs
- [x] Extract the god name from the skin name to allow for better file naming
- [x] Download wallpapers from the scraped links
- [ ] Add progress bar ([tqdm](https://github.com/tqdm/tqdm))
- [ ] Add command line arguments to:
    - [ ] Specify file names from/to which to read/write
    - [ ] Specify file name format for the wallpapers
    - [ ] Decide whether to scrape skins that don't have wallpapers
    - [ ] Switch between scraping and downloading
