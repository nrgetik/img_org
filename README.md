# img_org
Trivially organizes and renames some media files chronologically according to creation date/time available in metadata

## Usage
```
Usage: img_org.py [OPTIONS]

Options:
  -s, --source TEXT       Source path  [required]
  -d, --destination TEXT  Destination path  [required]
  -y, --yearly            Organize into yearly subfolders
  -m, --monthly           Organize into monthly subfolders (implies yearly)
```

### Install dependencies
```
pip-compile --output-file requirements.txt requirements.in
pip -i requirements.txt
```
### External requirements
Phil Harvey's excellent [ExifTool](https://www.sno.phy.queensu.ca/~phil/exiftool/)
