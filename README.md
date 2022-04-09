# Smitepaper
### Smite wallpaper scraper

### Process
- Grab all the slugs of posts with the tag `Update Notes` on the [https://www.smitegame.com/news/](https://www.smitegame.com/news/) page.
- The slugs are saved to `slugs.txt` and the second time the script is run and the file exists, the slugs are read from there.
- Iterate through each slug, visit every post and write the skin name, link to the image, the image size and the slug to `wallpapers.csv` if it's not there already.
- Note that some skins don't have links to the wallpapers, but they are still written to the csv file.
- The files are kept in this repo, so there is no need to repeat the process, unless it's out of date.
- To keep the csv file up to date, only keep the slugs from which to grab the new wallpapers. There shouldn't be any duplicates if you run the script twice in a row, but it will be significantly faster.

### TODOs
- [ ] Extract the god name from the skin name to allow for better file naming
- [ ] Download wallpapers from the scraped links
- [ ] Add command line arguments to:
    - [ ] Specify file names from/to which to read/write
    - [ ] Specify file names of the wallpapers (for the download function)
    - [ ] Decide whether to save skins that don't have wallpapers